package org.example.patterns;
public class BillingFacadeTest {
    public static void main(String[] args) {
        BillingFacade f = new BillingFacade();
        if (!f.submit("x").equals("wrote-billing:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
