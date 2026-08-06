package org.example.patterns;
public class CartProxyTest {
    public static void main(String[] args) {
        if (!new CartProxy(true).load("1").equals("real-cart:1")) throw new AssertionError();
        if (!new CartProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
