package org.example.patterns;
public class MetricsBuilderTest {
    public static void main(String[] args) {
        MetricsConfig cfg = new MetricsConfig.Builder().name("metrics-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("metrics-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
