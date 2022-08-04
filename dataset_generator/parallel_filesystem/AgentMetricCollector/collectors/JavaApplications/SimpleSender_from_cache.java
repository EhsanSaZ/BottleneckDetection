
import java.io.FileInputStream;
import java.io.IOException;
import java.net.Socket;
import java.io.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.concurrent.*;
import java.time.LocalDateTime; // Import the LocalDateTime class
import java.time.format.DateTimeFormatter; // Import the DateTimeFormatter class
// import javax.xml.bind.annotation.adapters.HexBinaryAdapter;


public class SimpleSender1 {
    private Socket s;

    static boolean allFileTransfersCompleted = false;
    static String destIp;

    static long totalTransferredBytes = 0;
    static long totalChecksumBytes = 0;
    long INTEGRITY_VERIFICATION_BLOCK_SIZE = 256 * 1024 * 1024;
    long startTime;
    boolean debug = false;

	int yy  = 0;
	int FileCount;

    public SimpleSender1(String host, int port) {
        try {
            s = new Socket(host, port);
            s.setSoTimeout(10000);
        } catch (Exception e) {
            System.out.println(e);
        }
    }
    public void sendFile(String path, int label) throws IOException {

//         new MonitorThread(label).start();
        startTime = System.currentTimeMillis();
        DataOutputStream dos = new DataOutputStream(s.getOutputStream());

        System.out.println("Will transfer from cache");

        long init2 = System.currentTimeMillis();

        byte[] buffer = new byte[1024 * 128];
        new Random().nextBytes(buffer);

        int n = buffer.length;
//        this.clearCache(path);
        while (true) {

            totalTransferredBytes += buffer.length;
            dos.write(buffer, 0, n);
			}

    }


    
    public static void main(String[] args) {
        destIp = args[0];
        int port = Integer.valueOf(args[1]);
        String path = args[2];
        int label = Integer.valueOf(args[3]);
        SimpleSender1 fc = new SimpleSender1(destIp, port);
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


