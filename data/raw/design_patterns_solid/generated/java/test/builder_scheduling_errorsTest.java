package org.example.patterns;
public class SchedulingBuilderTest {
    public static void main(String[] args) {
        SchedulingConfig cfg = new SchedulingConfig.Builder().name("scheduling-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("scheduling-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
