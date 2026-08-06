package org.example.patterns;
public class BillingFactoryTest {
    public static void main(String[] args) {
        BillingFactory f = new BillingFactory();
        if (!f.create("basic").operate().equals("basic-billing")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-billing")) throw new AssertionError();
        System.out.println("ok");
    }
}
