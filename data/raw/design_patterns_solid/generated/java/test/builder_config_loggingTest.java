package org.example.patterns;
public class ConfigBuilderTest {
    public static void main(String[] args) {
        ConfigConfig cfg = new ConfigConfig.Builder().name("config-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("config-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
