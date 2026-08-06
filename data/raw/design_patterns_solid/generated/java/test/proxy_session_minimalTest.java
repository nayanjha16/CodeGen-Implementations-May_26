package org.example.patterns;
public class SessionProxyTest {
    public static void main(String[] args) {
        if (!new SessionProxy(true).load("1").equals("real-session:1")) throw new AssertionError();
        if (!new SessionProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
