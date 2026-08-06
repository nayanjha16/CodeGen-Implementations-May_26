package org.example.patterns;
public class EmailBridgeTest {
    public static void main(String[] args) {
        EmailBridge b = new EmailAlertBridge(new EmailFileImpl());
        String out = b.send("x");
        if (!out.equals("file:email:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
