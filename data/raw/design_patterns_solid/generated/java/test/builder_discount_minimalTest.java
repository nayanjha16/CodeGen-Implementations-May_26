package org.example.patterns;
public class DiscountBuilderTest {
    public static void main(String[] args) {
        DiscountConfig cfg = new DiscountConfig.Builder().name("discount-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("discount-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
