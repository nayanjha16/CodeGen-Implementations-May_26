package org.example.patterns;
public class LoggingBuilderTest {
    public static void main(String[] args) {
        LoggingConfig cfg = new LoggingConfig.Builder().name("logging-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("logging-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
