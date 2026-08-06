package org.example.patterns;
public class BillingChainTest {
    public static void main(String[] args) {
        BillingHandler h = new BillingLowHandler();
        h.link(new BillingHighHandler());
        if (!h.handle(2, "m").equals("high-billing:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
