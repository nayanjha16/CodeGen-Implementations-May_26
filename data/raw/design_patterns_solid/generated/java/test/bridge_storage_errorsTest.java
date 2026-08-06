package org.example.patterns;
public class StorageBridgeTest {
    public static void main(String[] args) {
        StorageBridge b = new StorageAlertBridge(new StorageFileImpl());
        String out = b.send("x");
        if (!out.equals("file:storage:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
