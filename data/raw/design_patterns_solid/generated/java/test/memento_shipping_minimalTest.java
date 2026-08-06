package org.example.patterns;
public class ShippingMementoTest {
    public static void main(String[] args) {
        ShippingOriginator o = new ShippingOriginator();
        ShippingMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("shipping-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
