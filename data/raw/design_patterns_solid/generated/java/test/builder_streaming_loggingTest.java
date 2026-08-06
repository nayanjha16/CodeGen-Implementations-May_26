package org.example.patterns;
public class StreamingBuilderTest {
    public static void main(String[] args) {
        StreamingConfig cfg = new StreamingConfig.Builder().name("streaming-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("streaming-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
