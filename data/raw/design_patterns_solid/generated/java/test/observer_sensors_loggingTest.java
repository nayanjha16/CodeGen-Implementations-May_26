package org.example.patterns;
public class SensorsObserverTest {
    public static void main(String[] args) {
        SensorsSubject s = new SensorsSubject();
        SensorsListener l = new SensorsListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("sensors:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
