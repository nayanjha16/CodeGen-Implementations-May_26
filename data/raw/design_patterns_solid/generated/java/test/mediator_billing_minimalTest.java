package org.example.patterns;
public class BillingMediatorTest {
    public static void main(String[] args) {
        BillingMediator m = new BillingMediator();
        new BillingColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
