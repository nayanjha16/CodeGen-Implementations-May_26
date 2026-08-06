package org.example.patterns;
public class DiscountProxyTest {
    public static void main(String[] args) {
        if (!new DiscountProxy(true).load("1").equals("real-discount:1")) throw new AssertionError();
        if (!new DiscountProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
