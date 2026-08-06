package org.example.patterns;
public class ShippingMediatorTest {
    public static void main(String[] args) {
        ShippingMediator m = new ShippingMediator();
        new ShippingColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
