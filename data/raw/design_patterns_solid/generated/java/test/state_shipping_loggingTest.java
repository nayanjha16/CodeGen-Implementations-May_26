package org.example.patterns;
public class ShippingStateTest {
    public static void main(String[] args) {
        ShippingContext ctx = new ShippingContext();
        if (!ctx.request().equals("was-off-shipping")) throw new AssertionError();
        if (!ctx.request().equals("was-on-shipping")) throw new AssertionError();
        System.out.println("ok");
    }
}
