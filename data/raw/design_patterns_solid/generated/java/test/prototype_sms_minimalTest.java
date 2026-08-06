package org.example.patterns;
public class SmsPrototypeTest {
    public static void main(String[] args) {
        SmsPrototype a = new SmsPrototype("sms", 2);
        SmsPrototype b = a.copy();
        b.setLabel("sms-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
