package org.example.patterns;
public class DiscountChainTest {
    public static void main(String[] args) {
        DiscountHandler h = new DiscountLowHandler();
        h.link(new DiscountHighHandler());
        if (!h.handle(2, "m").equals("high-discount:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
