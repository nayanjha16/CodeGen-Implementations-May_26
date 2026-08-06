package org.example.patterns;
public class TaxObserverTest {
    public static void main(String[] args) {
        TaxSubject s = new TaxSubject();
        TaxListener l = new TaxListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("tax:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
