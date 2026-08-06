package org.example.patterns;
public class AnalyticsBuilderTest {
    public static void main(String[] args) {
        AnalyticsConfig cfg = new AnalyticsConfig.Builder().name("analytics-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("analytics-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
