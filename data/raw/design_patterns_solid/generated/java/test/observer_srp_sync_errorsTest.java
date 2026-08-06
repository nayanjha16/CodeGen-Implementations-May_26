package org.example.patterns;
public class SyncObserverTest {
    public static void main(String[] args) {
        SyncSubject s = new SyncSubject();
        SyncListener l = new SyncListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("sync:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
