package org.example.patterns;
public class BookingBridgeTest {
    public static void main(String[] args) {
        BookingBridge b = new BookingAlertBridge(new BookingFileImpl());
        String out = b.send("x");
        if (!out.equals("file:booking:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
