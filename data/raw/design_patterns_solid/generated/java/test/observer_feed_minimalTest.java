package org.example.patterns;
public class FeedObserverTest {
    public static void main(String[] args) {
        FeedSubject s = new FeedSubject();
        FeedListener l = new FeedListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("feed:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
