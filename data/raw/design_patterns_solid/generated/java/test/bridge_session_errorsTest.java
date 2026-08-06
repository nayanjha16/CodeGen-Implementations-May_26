package org.example.patterns;
public class SessionBridgeTest {
    public static void main(String[] args) {
        SessionBridge b = new SessionAlertBridge(new SessionFileImpl());
        String out = b.send("x");
        if (!out.equals("file:session:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
