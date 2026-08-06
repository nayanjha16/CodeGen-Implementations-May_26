package org.example.patterns;
public class CacheBuilderTest {
    public static void main(String[] args) {
        CacheConfig cfg = new CacheConfig.Builder().name("cache-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("cache-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
