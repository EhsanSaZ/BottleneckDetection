
import java.io.FileInputStream;
import java.io.IOException;
import java.net.Socket;
import java.io.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.net.*;
import java.util.concurrent.*;
import java.time.LocalDateTime; // Import the LocalDateTime class
import java.time.format.DateTimeFormatter; // Import the DateTimeFormatter class
// import javax.xml.bind.annotation.adapters.HexBinaryAdapter;


public class SimpleSender1 {
    private Socket s;

    static boolean allFileTransfersCompleted = false;
    static String destIp;

    List<FiverFile> files;
    LinkedBlockingQueue<FiverFile> checksumFiles;

    static long totalTransferredBytes = 0;
    static long totalChecksumBytes = 0;
    long INTEGRITY_VERIFICATION_BLOCK_SIZE = 256 * 1024 * 1024;
    long startTime;
    boolean debug = false;

	int yy  = 0;
	int FileCount;


    static LinkedBlockingQueue<Item> items = new LinkedBlockingQueue<>(10000);

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

    class Item {
        byte[] buffer;
        int length;

        public Item(byte[] buffer, int length){
            this.buffer =  Arrays.copyOf(buffer, length);
            this.length = length;
        }
    }

    public SimpleSender1(String host, int port, String localIP, int localPort) {
        try {
            if (localIP != ""){
                InetAddress localAddress = InetAddress.getByName(localIP);
                s = new Socket(host, port, localAddress, localPort);
                s.setSoTimeout(10000);
            }else{
                s = new Socket(host, port);
                s.setSoTimeout(10000);
            }

        } catch (Exception e) {
            System.out.println(e);
        }
    }
    public void clearCache(String path){
        // clear the cache for this file
            try {
                Process process = Runtime.getRuntime().exec("vmtouch -ve " + path);
                int exitVal = process.waitFor();
                if (exitVal != 0) {
                    System.out.println("Can't clear the cache");
                }
            } catch (IOException e) {
		        e.printStackTrace();
            } catch (InterruptedException e) {
		            e.printStackTrace();
	        }
    }
    public void sendFile(String path, int label) throws IOException {

//         new MonitorThread(label).start();
        startTime = System.currentTimeMillis();
        DataOutputStream dos = new DataOutputStream(s.getOutputStream());

        File file =new File(path);
        files = new LinkedList<>();

        List<FiverFile> originalfiles = new LinkedList<>();

        if(file.isDirectory()) {
            for (File f : file.listFiles()) {
                files.add(new FiverFile(f, 0, f.length()));
                originalfiles.add(new FiverFile(f, 0, f.length()));
            }
        } else {
            files.add(new FiverFile(file, 0, file.length()));
            originalfiles.add(new FiverFile(file, 0, file.length()));
        }
        System.out.println("Will transfer " + files.size()+ " files");
	    FileCount = files.size();
        long init2 = System.currentTimeMillis();
        //dos.writeLong(INTEGRITY_VERIFICATION_BLOCK_SIZE);
        dos.writeInt(FileCount);
        byte[] buffer = new byte[1024 * 128];
        int n;
//        this.clearCache(path);
        while (true) {
            FiverFile currentFile = null;
//             synchronized (files) {
//                 if (!files.isEmpty()) {
//                     currentFile = files.remove(0);
//                 }
//             }
            if (!files.isEmpty()) {
                currentFile = files.remove(0);
            }
//             if (currentFile == null) {
//                 try {
//                     Thread.sleep(100);
//                 } catch (InterruptedException e) {
//                     e.printStackTrace();
//                 }
//                 continue;
//             }
            this.clearCache(path + currentFile.file.getName());
            //send file metadata
            dos.writeUTF(currentFile.file.getName());
//             dos.writeLong(currentFile.offset);
            dos.writeLong(currentFile.length);
// 	        dos.writeInt(FileCount);

            long fileTransferStartTime = System.currentTimeMillis();

            FileInputStream fis = new FileInputStream(currentFile.file);
//             if (currentFile.offset > 0) {
//                 fis.getChannel().position(currentFile.offset);
//             }
            Long remaining = currentFile.length;
                while ((n = fis.read(buffer, 0, (int) Math.min((long)buffer.length, remaining))) > 0) {
                    remaining -= n;
                    totalTransferredBytes += n;
                    dos.write(buffer, 0, n);
                }
            fis.close();
            yy ++;
            System.out.println("FileCount: " + yy);
        	if (yy  == FileCount){
				// System.out.println("Checksum END File "  +  " time: " + (System.currentTimeMillis() - startTime) / 1000.0 + " seconds");
				// System.out.println("FileCount: " + FileCount);
                // allFileTransfersCompleted = true;
                // // break;
                // System.exit(0);

                for (FiverFile f : originalfiles) {
                    files.add(f);
                }
//                this.clearCache(path);
                yy=0;
			}

                   
        }
    }


    
    public static void main(String[] args) {
        destIp = args[0];
        int port = Integer.valueOf(args[1]);
        String path = args[2];
        int label = Integer.valueOf(args[3]);
        String sourceIP = "";
        int sourcePort = -1;
        try{
            sourceIP = args[4];
            sourcePort = Integer.valueOf(args[5]);
        } catch(Exception e){
            System.out.println("Using default local port and random local port");
        }
        SimpleSender1 fc = new SimpleSender1(destIp, port, sourceIP, sourcePort);
        try {
            fc.sendFile(path,label);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public class MonitorThread extends Thread {
        long lastTransferredBytes = 0;
        long lastChecksumBytes = 0;
        int label;
        String outputString ="";
        int count = 0;
        MonitorThread(int label){
            this.label = label;
        }

        @Override
        public void run() {
            try {
                while (!allFileTransfersCompleted) {
                    LocalDateTime myDateObj = LocalDateTime.now();
                    DateTimeFormatter myFormatObj = DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm:ss");
                    String formattedDate = myDateObj.format(myFormatObj);


                    double transferThrInMbps = ((totalTransferredBytes-lastTransferredBytes)*8)/(1024*1024);
                    // System.out.println(this.label+ " Network thr:" + transferThrInMbps + "MB/s");
                    outputString+=formattedDate + " "+this.label+ " Network thr:" + transferThrInMbps + "Mb/s\n";
                    lastTransferredBytes = totalTransferredBytes;
                    count+=1;
                    if(count%1==0){
                        new WriteThread(outputString).start();
                        outputString ="";
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
        
        WriteThread(String output){
            this.output = output;
        }

        @Override
        public void run() {
            try {
                BufferedWriter out = new BufferedWriter(new FileWriter("../normal_filesystem/SimpleSenderLog/Sender1_throughput.txt", true));
                out.write(this.output); 
                out.close(); 
            } catch (Exception e) {
                e.printStackTrace();
            }

        }
    }


}


