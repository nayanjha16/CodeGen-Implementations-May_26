package org.example.patterns;
public class HttpProxyTest {
    public static void main(String[] args) {
        if (!new HttpProxy(true).load("1").equals("real-http:1")) throw new AssertionError();
        if (!new HttpProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
