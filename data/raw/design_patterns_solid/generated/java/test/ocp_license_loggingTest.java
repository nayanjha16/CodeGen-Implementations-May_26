package org.example.patterns;
public class LicenseOcpTest {
    public static void main(String[] args) {
        if (new LicensePriceEngine(new LicenseTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
