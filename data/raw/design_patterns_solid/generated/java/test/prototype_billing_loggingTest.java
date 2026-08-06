package org.example.patterns;
public class BillingPrototypeTest {
    public static void main(String[] args) {
        BillingPrototype a = new BillingPrototype("billing", 2);
        BillingPrototype b = a.copy();
        b.setLabel("billing-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
