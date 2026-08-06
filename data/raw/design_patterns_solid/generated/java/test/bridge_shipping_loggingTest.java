package org.example.patterns;
public class ShippingBridgeTest {
    public static void main(String[] args) {
        ShippingBridge b = new ShippingAlertBridge(new ShippingFileImpl());
        String out = b.send("x");
        if (!out.equals("file:shipping:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
