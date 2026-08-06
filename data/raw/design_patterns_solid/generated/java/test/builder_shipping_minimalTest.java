package org.example.patterns;
public class ShippingBuilderTest {
    public static void main(String[] args) {
        ShippingConfig cfg = new ShippingConfig.Builder().name("shipping-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("shipping-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
