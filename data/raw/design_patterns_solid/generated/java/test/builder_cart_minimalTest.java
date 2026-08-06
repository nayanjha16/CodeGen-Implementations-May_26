package org.example.patterns;
public class CartBuilderTest {
    public static void main(String[] args) {
        CartConfig cfg = new CartConfig.Builder().name("cart-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("cart-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
