package org.example.patterns;
public class CanvasObserverTest {
    public static void main(String[] args) {
        CanvasSubject s = new CanvasSubject();
        CanvasListener l = new CanvasListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("canvas:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
