package org.example.patterns;
public class AnalyticsBridgeTest {
    public static void main(String[] args) {
        AnalyticsBridge b = new AnalyticsAlertBridge(new AnalyticsFileImpl());
        String out = b.send("x");
        if (!out.equals("file:analytics:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
