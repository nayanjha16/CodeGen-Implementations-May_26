package org.example.patterns;
public class PaymentsBridgeTest {
    public static void main(String[] args) {
        PaymentsBridge b = new PaymentsAlertBridge(new PaymentsFileImpl());
        String out = b.send("x");
        if (!out.equals("file:payments:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
