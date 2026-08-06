package org.example.patterns;
public class BillingObserverTest {
    public static void main(String[] args) {
        BillingSubject s = new BillingSubject();
        BillingListener l = new BillingListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("billing:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
