package org.example.patterns;
public class TaxBridgeTest {
    public static void main(String[] args) {
        TaxBridge b = new TaxAlertBridge(new TaxFileImpl());
        String out = b.send("x");
        if (!out.equals("file:tax:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
