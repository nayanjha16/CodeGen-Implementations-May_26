package org.example.patterns;
public class SyncBridgeTest {
    public static void main(String[] args) {
        SyncBridge b = new SyncAlertBridge(new SyncFileImpl());
        String out = b.send("x");
        if (!out.equals("file:sync:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
