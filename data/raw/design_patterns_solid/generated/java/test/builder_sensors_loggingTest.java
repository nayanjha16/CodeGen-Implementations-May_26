package org.example.patterns;
public class SensorsBuilderTest {
    public static void main(String[] args) {
        SensorsConfig cfg = new SensorsConfig.Builder().name("sensors-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("sensors-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
