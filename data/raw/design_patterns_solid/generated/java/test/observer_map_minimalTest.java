package org.example.patterns;
public class MapObserverTest {
    public static void main(String[] args) {
        MapSubject s = new MapSubject();
        MapListener l = new MapListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("map:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
