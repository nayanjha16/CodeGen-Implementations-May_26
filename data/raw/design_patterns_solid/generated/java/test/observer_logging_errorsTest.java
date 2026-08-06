package org.example.patterns;
public class LoggingObserverTest {
    public static void main(String[] args) {
        LoggingSubject s = new LoggingSubject();
        LoggingListener l = new LoggingListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("logging:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
