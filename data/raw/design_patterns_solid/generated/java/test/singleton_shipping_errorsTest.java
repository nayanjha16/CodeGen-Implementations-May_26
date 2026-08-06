package org.example.patterns;
public class ShippingSingletonTest {
    public static void main(String[] args) {
        ShippingSingleton a = ShippingSingleton.getInstance();
        ShippingSingleton b = ShippingSingleton.getInstance();
        a.setValue("shipping-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("shipping-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
