package org.example.patterns;
public class ProfileProxyTest {
    public static void main(String[] args) {
        if (!new ProfileProxy(true).load("1").equals("real-profile:1")) throw new AssertionError();
        if (!new ProfileProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
