package org.example.patterns;
public class WalletBridgeTest {
    public static void main(String[] args) {
        WalletBridge b = new WalletAlertBridge(new WalletFileImpl());
        String out = b.send("x");
        if (!out.equals("file:wallet:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
