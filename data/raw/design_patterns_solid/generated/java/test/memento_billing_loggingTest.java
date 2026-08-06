package org.example.patterns;
public class BillingMementoTest {
    public static void main(String[] args) {
        BillingOriginator o = new BillingOriginator();
        BillingMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("billing-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
