package org.example.patterns;
public class BackupBridgeTest {
    public static void main(String[] args) {
        BackupBridge b = new BackupAlertBridge(new BackupFileImpl());
        String out = b.send("x");
        if (!out.equals("file:backup:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
