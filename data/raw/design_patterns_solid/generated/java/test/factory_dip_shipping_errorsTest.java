package org.example.patterns;
public class ShippingFactoryTest {
    public static void main(String[] args) {
        ShippingFactory f = new ShippingFactory();
        if (!f.create("basic").operate().equals("basic-shipping")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-shipping")) throw new AssertionError();
        System.out.println("ok");
    }
}
