package org.example.patterns;
public class TodoObserverTest {
    public static void main(String[] args) {
        TodoSubject s = new TodoSubject();
        TodoListener l = new TodoListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("todo:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
