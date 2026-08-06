package org.example.patterns;
public class ShippingChainTest {
    public static void main(String[] args) {
        ShippingHandler h = new ShippingLowHandler();
        h.link(new ShippingHighHandler());
        if (!h.handle(2, "m").equals("high-shipping:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
