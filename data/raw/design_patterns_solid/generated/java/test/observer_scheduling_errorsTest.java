package org.example.patterns;
public class SchedulingObserverTest {
    public static void main(String[] args) {
        SchedulingSubject s = new SchedulingSubject();
        SchedulingListener l = new SchedulingListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("scheduling:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
