package org.example.patterns;
public class ShippingSrpTest {
    public static void main(String[] args) {
        ShippingRecord r = new ShippingRecord("a", 3);
        if (!new ShippingFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
