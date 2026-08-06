package org.example.patterns;
public class DiscountOcpTest {
    public static void main(String[] args) {
        if (new DiscountPriceEngine(new DiscountTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
