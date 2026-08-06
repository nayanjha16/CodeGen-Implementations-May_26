package org.example.patterns;
public class DatabaseObserverTest {
    public static void main(String[] args) {
        DatabaseSubject s = new DatabaseSubject();
        DatabaseListener l = new DatabaseListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("database:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
