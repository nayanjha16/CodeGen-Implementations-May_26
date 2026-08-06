package org.example.patterns;
public class ReviewBuilderTest {
    public static void main(String[] args) {
        ReviewConfig cfg = new ReviewConfig.Builder().name("review-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("review-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
