package org.example.patterns;
public class BillingStateTest {
    public static void main(String[] args) {
        BillingContext ctx = new BillingContext();
        if (!ctx.request().equals("was-off-billing")) throw new AssertionError();
        if (!ctx.request().equals("was-on-billing")) throw new AssertionError();
        System.out.println("ok");
    }
}
