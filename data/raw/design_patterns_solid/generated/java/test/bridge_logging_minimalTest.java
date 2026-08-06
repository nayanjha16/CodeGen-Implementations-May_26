package org.example.patterns;
public class LoggingBridgeTest {
    public static void main(String[] args) {
        LoggingBridge b = new LoggingAlertBridge(new LoggingFileImpl());
        String out = b.send("x");
        if (!out.equals("file:logging:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
