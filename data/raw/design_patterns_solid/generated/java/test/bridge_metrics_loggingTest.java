package org.example.patterns;
public class MetricsBridgeTest {
    public static void main(String[] args) {
        MetricsBridge b = new MetricsAlertBridge(new MetricsFileImpl());
        String out = b.send("x");
        if (!out.equals("file:metrics:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
