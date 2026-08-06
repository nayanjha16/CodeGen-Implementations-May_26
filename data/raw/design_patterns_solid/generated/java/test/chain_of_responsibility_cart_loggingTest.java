package org.example.patterns;
public class CartChainTest {
    public static void main(String[] args) {
        CartHandler h = new CartLowHandler();
        h.link(new CartHighHandler());
        if (!h.handle(2, "m").equals("high-cart:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
