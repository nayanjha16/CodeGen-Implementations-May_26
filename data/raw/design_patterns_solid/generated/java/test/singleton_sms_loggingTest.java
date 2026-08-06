package org.example.patterns;
public class SmsSingletonTest {
    public static void main(String[] args) {
        SmsSingleton a = SmsSingleton.getInstance();
        SmsSingleton b = SmsSingleton.getInstance();
        a.setValue("sms-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("sms-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
