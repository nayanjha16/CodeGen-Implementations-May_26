package org.example.patterns;
public class CanvasBuilderTest {
    public static void main(String[] args) {
        CanvasConfig cfg = new CanvasConfig.Builder().name("canvas-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("canvas-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
