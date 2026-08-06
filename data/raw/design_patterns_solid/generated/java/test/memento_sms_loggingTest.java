package org.example.patterns;
public class SmsMementoTest {
    public static void main(String[] args) {
        SmsOriginator o = new SmsOriginator();
        SmsMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("sms-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
