package org.example.patterns;
public class SchedulingBridgeTest {
    public static void main(String[] args) {
        SchedulingBridge b = new SchedulingAlertBridge(new SchedulingFileImpl());
        String out = b.send("x");
        if (!out.equals("file:scheduling:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
