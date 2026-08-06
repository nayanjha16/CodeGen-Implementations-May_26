package org.example.patterns;
public class SmsFactoryTest {
    public static void main(String[] args) {
        SmsFactory f = new SmsFactory();
        if (!f.create("basic").operate().equals("basic-sms")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-sms")) throw new AssertionError();
        System.out.println("ok");
    }
}
