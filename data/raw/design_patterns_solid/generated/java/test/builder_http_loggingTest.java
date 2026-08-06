package org.example.patterns;
public class HttpBuilderTest {
    public static void main(String[] args) {
        HttpConfig cfg = new HttpConfig.Builder().name("http-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("http-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
