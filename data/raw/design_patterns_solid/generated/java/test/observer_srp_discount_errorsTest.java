package org.example.patterns;
public class DiscountObserverTest {
    public static void main(String[] args) {
        DiscountSubject s = new DiscountSubject();
        DiscountListener l = new DiscountListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("discount:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
