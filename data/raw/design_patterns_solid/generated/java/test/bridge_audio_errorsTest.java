package org.example.patterns;
public class AudioBridgeTest {
    public static void main(String[] args) {
        AudioBridge b = new AudioAlertBridge(new AudioFileImpl());
        String out = b.send("x");
        if (!out.equals("file:audio:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
