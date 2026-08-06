package org.example.patterns;
public class LicenseFactoryTest {
    public static void main(String[] args) {
        LicenseFactory f = new LicenseFactory();
        if (!f.create("basic").operate().equals("basic-license")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-license")) throw new AssertionError();
        System.out.println("ok");
    }
}
