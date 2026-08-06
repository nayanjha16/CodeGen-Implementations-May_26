package org.example.patterns;
public class SmsObserverTest {
    public static void main(String[] args) {
        SmsSubject s = new SmsSubject();
        SmsListener l = new SmsListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("sms:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
