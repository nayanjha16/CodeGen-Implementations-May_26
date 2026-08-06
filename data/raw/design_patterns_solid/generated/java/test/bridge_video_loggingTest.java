package org.example.patterns;
public class VideoBridgeTest {
    public static void main(String[] args) {
        VideoBridge b = new VideoAlertBridge(new VideoFileImpl());
        String out = b.send("x");
        if (!out.equals("file:video:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
