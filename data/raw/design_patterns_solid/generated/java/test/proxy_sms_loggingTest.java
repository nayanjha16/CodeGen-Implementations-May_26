package org.example.patterns;
public class SmsProxyTest {
    public static void main(String[] args) {
        if (!new SmsProxy(true).load("1").equals("real-sms:1")) throw new AssertionError();
        if (!new SmsProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
