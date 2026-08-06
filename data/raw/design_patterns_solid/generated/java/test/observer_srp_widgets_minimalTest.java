package org.example.patterns;
public class WidgetsObserverTest {
    public static void main(String[] args) {
        WidgetsSubject s = new WidgetsSubject();
        WidgetsListener l = new WidgetsListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("widgets:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
