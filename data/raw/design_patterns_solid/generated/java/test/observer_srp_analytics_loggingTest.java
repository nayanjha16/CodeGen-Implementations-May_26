package org.example.patterns;
public class AnalyticsObserverTest {
    public static void main(String[] args) {
        AnalyticsSubject s = new AnalyticsSubject();
        AnalyticsListener l = new AnalyticsListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("analytics:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
