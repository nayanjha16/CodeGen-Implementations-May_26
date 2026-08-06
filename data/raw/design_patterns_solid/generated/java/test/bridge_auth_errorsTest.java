package org.example.patterns;
public class AuthBridgeTest {
    public static void main(String[] args) {
        AuthBridge b = new AuthAlertBridge(new AuthFileImpl());
        String out = b.send("x");
        if (!out.equals("file:auth:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
