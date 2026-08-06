package org.example.patterns;
public class SessionObserverTest {
    public static void main(String[] args) {
        SessionSubject s = new SessionSubject();
        SessionListener l = new SessionListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("session:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
