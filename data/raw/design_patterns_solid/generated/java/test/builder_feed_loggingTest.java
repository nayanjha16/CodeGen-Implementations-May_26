package org.example.patterns;
public class FeedBuilderTest {
    public static void main(String[] args) {
        FeedConfig cfg = new FeedConfig.Builder().name("feed-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("feed-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
