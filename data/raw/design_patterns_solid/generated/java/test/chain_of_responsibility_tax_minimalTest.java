package org.example.patterns;
public class TaxChainTest {
    public static void main(String[] args) {
        TaxHandler h = new TaxLowHandler();
        h.link(new TaxHighHandler());
        if (!h.handle(2, "m").equals("high-tax:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
