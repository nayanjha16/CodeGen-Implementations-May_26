package org.example.patterns;
public class LicenseProxyTest {
    public static void main(String[] args) {
        if (!new LicenseProxy(true).load("1").equals("real-license:1")) throw new AssertionError();
        if (!new LicenseProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
