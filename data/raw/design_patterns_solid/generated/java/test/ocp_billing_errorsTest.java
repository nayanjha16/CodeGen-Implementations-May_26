package org.example.patterns;
public class BillingOcpTest {
    public static void main(String[] args) {
        if (new BillingPriceEngine(new BillingTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
