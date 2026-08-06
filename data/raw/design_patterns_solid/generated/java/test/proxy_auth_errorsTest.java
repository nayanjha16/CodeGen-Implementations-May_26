package org.example.patterns;
public class AuthProxyTest {
    public static void main(String[] args) {
        if (!new AuthProxy(true).load("1").equals("real-auth:1")) throw new AssertionError();
        if (!new AuthProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
