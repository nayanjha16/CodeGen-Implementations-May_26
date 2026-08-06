package org.example.patterns;
public class CacheObserverTest {
    public static void main(String[] args) {
        CacheSubject s = new CacheSubject();
        CacheListener l = new CacheListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("cache:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
