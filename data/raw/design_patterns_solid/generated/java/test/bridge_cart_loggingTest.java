package org.example.patterns;
public class CartBridgeTest {
    public static void main(String[] args) {
        CartBridge b = new CartAlertBridge(new CartFileImpl());
        String out = b.send("x");
        if (!out.equals("file:cart:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
