package org.example.patterns;
public class LicensePrototypeTest {
    public static void main(String[] args) {
        LicensePrototype a = new LicensePrototype("license", 2);
        LicensePrototype b = a.copy();
        b.setLabel("license-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
