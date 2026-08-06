package org.example.patterns;
public class BackupDipTest {
    public static void main(String[] args) {
        String out = new BackupAppService(new BackupHttpGateway()).publish("p");
        if (!out.equals("http-backup:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
