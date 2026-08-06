package org.example.patterns;
public class StorageObserverTest {
    public static void main(String[] args) {
        StorageSubject s = new StorageSubject();
        StorageListener l = new StorageListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("storage:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
