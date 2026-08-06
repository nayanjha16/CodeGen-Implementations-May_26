package org.example.patterns;
public class SmsBridgeTest {
    public static void main(String[] args) {
        SmsBridge b = new SmsAlertBridge(new SmsFileImpl());
        String out = b.send("x");
        if (!out.equals("file:sms:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
