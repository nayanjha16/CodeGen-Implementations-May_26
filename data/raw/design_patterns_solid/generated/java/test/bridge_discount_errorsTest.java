package org.example.patterns;
public class DiscountBridgeTest {
    public static void main(String[] args) {
        DiscountBridge b = new DiscountAlertBridge(new DiscountFileImpl());
        String out = b.send("x");
        if (!out.equals("file:discount:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
