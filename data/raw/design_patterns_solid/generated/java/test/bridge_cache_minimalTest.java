package org.example.patterns;
public class CacheBridgeTest {
    public static void main(String[] args) {
        CacheBridge b = new CacheAlertBridge(new CacheFileImpl());
        String out = b.send("x");
        if (!out.equals("file:cache:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
