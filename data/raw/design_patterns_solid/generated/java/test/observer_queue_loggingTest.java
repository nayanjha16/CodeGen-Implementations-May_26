package org.example.patterns;
public class QueueObserverTest {
    public static void main(String[] args) {
        QueueSubject s = new QueueSubject();
        QueueListener l = new QueueListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("queue:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
