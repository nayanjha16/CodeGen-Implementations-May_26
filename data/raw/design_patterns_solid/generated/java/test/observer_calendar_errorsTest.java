package org.example.patterns;
public class CalendarObserverTest {
    public static void main(String[] args) {
        CalendarSubject s = new CalendarSubject();
        CalendarListener l = new CalendarListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("calendar:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
