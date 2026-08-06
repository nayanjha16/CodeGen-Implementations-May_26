package org.example.patterns;
public class ShippingOcpTest {
    public static void main(String[] args) {
        if (new ShippingPriceEngine(new ShippingTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
