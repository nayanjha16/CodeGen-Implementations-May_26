package org.example.patterns;
public class ShippingStrategyTest {
    public static void main(String[] args) {
        ShippingContext ctx = new ShippingContext(new ShippingDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
