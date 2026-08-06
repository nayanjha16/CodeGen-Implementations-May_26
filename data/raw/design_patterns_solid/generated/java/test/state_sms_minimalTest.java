package org.example.patterns;
public class SmsStateTest {
    public static void main(String[] args) {
        SmsContext ctx = new SmsContext();
        if (!ctx.request().equals("was-off-sms")) throw new AssertionError();
        if (!ctx.request().equals("was-on-sms")) throw new AssertionError();
        System.out.println("ok");
    }
}
