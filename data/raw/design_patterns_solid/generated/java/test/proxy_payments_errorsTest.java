package org.example.patterns;
public class PaymentsProxyTest {
    public static void main(String[] args) {
        if (!new PaymentsProxy(true).load("1").equals("real-payments:1")) throw new AssertionError();
        if (!new PaymentsProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
