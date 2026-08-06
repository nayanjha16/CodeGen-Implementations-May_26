package org.example.patterns;
public class ReviewBridgeTest {
    public static void main(String[] args) {
        ReviewBridge b = new ReviewAlertBridge(new ReviewFileImpl());
        String out = b.send("x");
        if (!out.equals("file:review:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
