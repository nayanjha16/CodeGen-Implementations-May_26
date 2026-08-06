package org.example.patterns;
public class AnalyticsDipTest {
    public static void main(String[] args) {
        String out = new AnalyticsAppService(new AnalyticsHttpGateway()).publish("p");
        if (!out.equals("http-analytics:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
