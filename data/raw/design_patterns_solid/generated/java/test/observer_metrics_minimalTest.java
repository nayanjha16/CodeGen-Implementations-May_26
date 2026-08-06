package org.example.patterns;
public class MetricsObserverTest {
    public static void main(String[] args) {
        MetricsSubject s = new MetricsSubject();
        MetricsListener l = new MetricsListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("metrics:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
