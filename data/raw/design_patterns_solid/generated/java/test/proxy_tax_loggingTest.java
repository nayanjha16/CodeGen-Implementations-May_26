package org.example.patterns;
public class TaxProxyTest {
    public static void main(String[] args) {
        if (!new TaxProxy(true).load("1").equals("real-tax:1")) throw new AssertionError();
        if (!new TaxProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
