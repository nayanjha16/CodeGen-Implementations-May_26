package org.example.patterns;
public class MapBuilderTest {
    public static void main(String[] args) {
        MapConfig cfg = new MapConfig.Builder().name("map-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("map-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
