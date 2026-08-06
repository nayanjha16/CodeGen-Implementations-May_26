package org.example.patterns;
public class ReviewObserverTest {
    public static void main(String[] args) {
        ReviewSubject s = new ReviewSubject();
        ReviewListener l = new ReviewListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("review:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
