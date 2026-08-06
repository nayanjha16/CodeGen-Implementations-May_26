package org.example.patterns;
public class NotificationsObserverTest {
    public static void main(String[] args) {
        NotificationsSubject s = new NotificationsSubject();
        NotificationsListener l = new NotificationsListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("notifications:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
