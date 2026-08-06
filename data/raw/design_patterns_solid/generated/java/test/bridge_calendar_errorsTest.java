package org.example.patterns;
public class CalendarBridgeTest {
    public static void main(String[] args) {
        CalendarBridge b = new CalendarAlertBridge(new CalendarFileImpl());
        String out = b.send("x");
        if (!out.equals("file:calendar:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
