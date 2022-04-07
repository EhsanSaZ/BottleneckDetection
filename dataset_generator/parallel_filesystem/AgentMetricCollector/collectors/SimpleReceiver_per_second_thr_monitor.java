// import javax.xml.bind.annotation.adapters.HexBinaryAdapter;
import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.Random;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;


public class SimpleReceiver_per_second_thr_monitor extends Thread{

    private ServerSocket ss;
    static AtomicBoolean allTransfersCompleted = new AtomicBoolean(false);
    static boolean connectionEstablished = false;
    static String baseDir = "/lustre/receiverDataDir/dstData/";
    static String thrSavingDir = "./SimpleReceiverPerSecondMonitor/";

    static long totalTransferredBytes = 0L;
    static long totalChecksumBytes = 0L;
    long INTEGRITY_VERIFICATION_BLOCK_SIZE = 256 *1024 * 1024;

    boolean debug = false;
    long startTime;
   	int yy  = 0;
	int FileCount;
    static String label = "default_label";

    static LinkedBlockingQueue<Item> items = new LinkedBlockingQueue<>(10000);

    class Item {
        byte[] buffer;
        int length;

        public Item(byte[] buffer, int length){
            this.buffer = Arrays.copyOf(buffer, length);
            this.length = length;
        }
    }

    public class FiverFile {
        public FiverFile(File file, long offset, long length) {
            this.file = file;
            this.offset = offset;
            this.length = length;
        }
        File file;
        Long offset;
        Long length;
    }


    public SimpleReceiver_per_second_thr_monitor(int port, String baseDir, String label) {
        try {
            ss = new ServerSocket(port);
            baseDir = baseDir;
            label = label;
            File o_dir = new File(thrSavingDir);
            if (!o_dir.exists()){
                o_dir.mkdirs();
            }
            System.out.println("Server Socket start listening on " + ss.getInetAddress() + " port: " + ss.getLocalPort() + " with label: " + label);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void run() {
        while (true) {
            try {
                Socket clientSock = ss.accept();
                // clientSock.setSoTimeout(10000);
                System.out.println("Connection established from  " + clientSock.getInetAddress());
                connectionEstablished = true;
                saveFile(clientSock, label);
            } catch (IOException e) {
                e.printStackTrace();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

    }

    private void saveFile(Socket clientSock, String label) throws IOException, InterruptedException {
        new MonitorThread(label).start();

        // startTime = System.currentTimeMillis();
        DataInputStream dataInputStream  = new DataInputStream(clientSock.getInputStream());
        //INTEGRITY_VERIFICATION_BLOCK_SIZE = dataInputStream.readLong();
        FileCount = dataInputStream.readInt();
        allTransfersCompleted.set(false);
        totalTransferredBytes = 0L;
        totalChecksumBytes = 0L;

        // long init2 = System.currentTimeMillis();

        
        File o_dir = new File(baseDir);
        if (!o_dir.exists()){
            o_dir.mkdirs();
        }
        byte[] buffer = new byte[1024 * 128];
        while(true) {
            String fileName = dataInputStream.readUTF();
//             long offset = dataInputStream.readLong();
            long fileSize = dataInputStream.readLong();
// 		    FileCount = dataInputStream.readInt();
            BufferedOutputStream file_out = new BufferedOutputStream(new FileOutputStream(baseDir + fileName));
//             RandomAccessFile randomAccessFile = new RandomAccessFile(baseDir + fileName, "rw");

//             if (offset > 0) {
//                 randomAccessFile.getChannel().position(offset);
//             }
            long remaining = fileSize;
            int read = 0;
            // long transferStartTime = System.currentTimeMillis();
            while (remaining > 0) {
                read = dataInputStream.read(buffer, 0, (int) Math.min(buffer.length, remaining));
                if (read == -1)
                    break;
                totalTransferredBytes += read;
                remaining -= read;
//                 System.out.println("Writing file " + fileName + " into dir " + baseDir);
//                 randomAccessFile.write(buffer, 0, read);
                file_out.write(buffer, 0, read);
            }
//             randomAccessFile.close();
            file_out.flush();
            file_out.close();
			yy ++;
            if (read == -1) {
                connectionEstablished = false;
                totalTransferredBytes = 0;
                yy = 0;
                System.out.println("Read -1, closing the connection...");
                return;
            }
//             System.out.println("FileCount: " + FileCount);
        	if (yy  % FileCount == 0){
				// System.out.println("Checksum END File "  +  " time: " + (System.currentTimeMillis() - startTime) / 1000.0 + " seconds");
                System.out.println("FileCount: " + FileCount + " round " + ((yy/FileCount) - 1) + " finished");
				// System.exit(0);
			}

	   }

    }

    public static void main (String[] args) {
        if (args.length > 0) {
            baseDir = args[0];
        }
        int port = 50505;
//        String label = "default_label";
        if (args.length > 1) {
            port = Integer.valueOf(args[1]);
        }
        if (args.length > 2) {
            label = args[2];
        }
        SimpleReceiver_per_second_thr_monitor fs = new SimpleReceiver_per_second_thr_monitor(port, baseDir, label);
        fs.start();
    }

    public class MonitorThread extends Thread {
        long lastTransferredBytes = 0;
        String label;
        String outputString ="";
        int count = 0;
        MonitorThread(String label){
            this.label = label;
        }
        @Override
        public void run() {
            try {
                 while (connectionEstablished) {
                     LocalDateTime myDateObj = LocalDateTime.now();
                     DateTimeFormatter myFormatObj = DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm:ss");
                     String formattedDate = myDateObj.format(myFormatObj);
//                    System.out.println(totalTransferredBytes-lastTransferredBytes);
                    double transferThrInGbps = ((totalTransferredBytes-lastTransferredBytes)*8.0)/(1024*1024*1024);
//                    System.out.println(this.label+ " Network thr:" + transferThrInGbps + " Gbps/s");
                    outputString += String.format("%s,%s,%s\n", formattedDate, this.label, transferThrInGbps);
//                     outputString+=formattedDate + " "+this.label+ " Network thr:" + transferThrInMbps + "Mb/s\n";
                     lastTransferredBytes = totalTransferredBytes;
                     count+=1;
                     if(count%5==0){
//                         System.out.println(outputString);
                         new WriteThread(outputString, thrSavingDir, label).start();
                         outputString ="";
                         count=0;
                     }
                     Thread.sleep(1000);
                 }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

        }
    }

    public class WriteThread extends Thread {
        String output;
        String savingDir;
        String label;
        WriteThread(String output, String savingDir, String label){
            this.output = output;
            this.savingDir = savingDir;
            this.label = label;
        }

        @Override
        public void run() {
            try {
                BufferedWriter out = new BufferedWriter(new FileWriter(String.format("%sthroughout_label_%s.csv", savingDir, label), true));
                out.write(this.output);
                out.close();
            } catch (Exception e) {
                e.printStackTrace();
            }

        }
    }
}



