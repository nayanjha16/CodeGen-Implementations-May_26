package org.example.patterns;
public class ShippingPrototypeTest {
    public static void main(String[] args) {
        ShippingPrototype a = new ShippingPrototype("shipping", 2);
        ShippingPrototype b = a.copy();
        b.setLabel("shipping-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
