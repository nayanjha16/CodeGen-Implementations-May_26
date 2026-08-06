package org.example.patterns;
public class EmailProxyTest {
    public static void main(String[] args) {
        if (!new EmailProxy(true).load("1").equals("real-email:1")) throw new AssertionError();
        if (!new EmailProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
