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

public class SimpleReceiver1 extends Thread{

    private ServerSocket ss;
    static AtomicBoolean allTransfersCompleted = new AtomicBoolean(false);
    static String baseDir = "/lustre/receiverDataDir/dstData/";
    static String thrSavingDir = "./SimpleReceiver1/receiverThroughputLog/";

    static long totalTransferredBytes = 0L;
    static long totalChecksumBytes = 0L;
    long INTEGRITY_VERIFICATION_BLOCK_SIZE = 256 *1024 * 1024;

    boolean debug = false;
    long startTime;
   	int yy  = 0;
	int FileCount;
    int label = 0;

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


    public SimpleReceiver1(int port, String baseDir, int label) {
        try {
            ss = new ServerSocket(port);
            baseDir = baseDir;
            label = label;
            File o_dir = new File(thrSavingDir);
            if (!o_dir.exists()){
                o_dir.mkdirs();
            }
            System.out.println("Server Socket start listening on " + ss.getInetAddress() + " port: " + ss.getLocalPort());
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
                saveFile(clientSock, label);
            } catch (IOException e) {
                e.printStackTrace();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

    }

    private void saveFile(Socket clientSock, int label) throws IOException, InterruptedException {


        // startTime = System.currentTimeMillis();
        DataInputStream dataInputStream  = new DataInputStream(clientSock.getInputStream());
        INTEGRITY_VERIFICATION_BLOCK_SIZE = dataInputStream.readLong();

        allTransfersCompleted.set(false);
        totalTransferredBytes = 0L;
        totalChecksumBytes = 0L;

        long lastTransferredBytes = 0;
        long roundTransferStartTime = System.currentTimeMillis();
        // long init2 = System.currentTimeMillis();

        File o_dir = new File(baseDir);
        if (!o_dir.exists()){
            o_dir.mkdirs();
        }
        byte[] buffer = new byte[1024 * 1024];
        while(true) {
            String fileName = dataInputStream.readUTF();
            long offset = dataInputStream.readLong();
            long fileSize = dataInputStream.readLong();
		    FileCount = dataInputStream.readInt();
            RandomAccessFile randomAccessFile = new RandomAccessFile(baseDir + fileName, "rw");
            if (offset > 0) {
                randomAccessFile.getChannel().position(offset);
            }
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
                randomAccessFile.write(buffer, 0, read);
            }
            randomAccessFile.close();
			yy ++;
            System.out.println("FileCount: " + FileCount + " round " + (yy/ (FileCount+1)) + " file " + yy);
            if (read == -1) {
                long roundTransferFinishTime = System.currentTimeMillis();
                long transferTime_sec = (roundTransferFinishTime - roundTransferStartTime);
//                roundTransferStartTime = System.currentTimeMillis();
                LocalDateTime myDateObj = LocalDateTime.now();
                DateTimeFormatter myFormatObj = DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm:ss");
                String formattedDate = myDateObj.format(myFormatObj);
                new WriteThread(
                        String.format("%s,%d,%f\n", formattedDate, this.label, (totalTransferredBytes * 8 * 1000.0)/ (1024 * 1024 * 1024* transferTime_sec)),
                        thrSavingDir,
                        label).start();
//                System.out.println("Read -1, closing the connection...");
//                System.out.println("Size: " + (totalTransferredBytes * 8)/ (1024 * 1024 * 1024));
//                System.out.println("Time: " + transferTime_sec);
//                System.out.println("Throughput is: " + (totalTransferredBytes * 8 * 1000.0)/ (1024 * 1024 * 1024* transferTime_sec));
                // TODO BUG
                totalTransferredBytes = 0;
                yy = 0;
                return;
            }
//             System.out.println("FileCount: " + FileCount);
        	if (yy  % FileCount == 0){
                // System.out.println("Checksum END File "  +  " time: " + (System.currentTimeMillis() - startTime) / 1000.0 + " seconds");
                System.out.println("FileCount: " + FileCount + " round " + ((yy/FileCount) - 1) + " finished");

                long roundTransferFinishTime = System.currentTimeMillis();
                long transferTime_sec = (roundTransferFinishTime - roundTransferStartTime);

                LocalDateTime myDateObj = LocalDateTime.now();
                DateTimeFormatter myFormatObj = DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm:ss");
                String formattedDate = myDateObj.format(myFormatObj);
                new WriteThread(
                        String.format("%s,%d,%f\n", formattedDate, this.label, (totalTransferredBytes * 8 * 1000.0)/ (1024 * 1024 * 1024* transferTime_sec)),
                        thrSavingDir,
                        label).start();
//                System.out.println("Size: " + (totalTransferredBytes * 8)/ (1024 * 1024 * 1024));
//                System.out.println("Time: " + transferTime_sec);
//                System.out.println("Throughput is: " + (totalTransferredBytes * 8 * 1000.0)/ (1024 * 1024 * 1024 * transferTime_sec));

                roundTransferStartTime = System.currentTimeMillis();
                totalTransferredBytes = 0;
				// System.exit(0);
			}

	   }

    }

    




    public static void main (String[] args) {
        if (args.length > 0) {
            baseDir = args[0];
        }
        int port = 50505;
        int label = 0;
        if (args.length > 1) {
            port = Integer.valueOf(args[1]);
        }
        if (args.length > 2) {
            label = Integer.valueOf(args[2]);
        }
        SimpleReceiver1 fs = new SimpleReceiver1(port, baseDir, label);
        fs.start();
    }

    public class WriteThread extends Thread {
        String output;
        String savingDir;
        int label;
        WriteThread(String output, String savingDir, int label){
            this.output = output;
            this.savingDir = savingDir;
            this.label = label;
        }

        @Override
        public void run() {
            try {
                BufferedWriter out = new BufferedWriter(new FileWriter(String.format("%slabel_%s_throughout.csv", savingDir, label), true));
                out.write(this.output);
                out.close();
            } catch (Exception e) {
                e.printStackTrace();
            }

        }
    }

}


