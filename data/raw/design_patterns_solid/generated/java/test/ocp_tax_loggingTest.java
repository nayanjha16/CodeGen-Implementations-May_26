package org.example.patterns;
public class TaxOcpTest {
    public static void main(String[] args) {
        if (new TaxPriceEngine(new TaxTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
