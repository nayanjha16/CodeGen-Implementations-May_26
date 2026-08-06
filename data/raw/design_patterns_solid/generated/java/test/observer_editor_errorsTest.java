package org.example.patterns;
public class EditorObserverTest {
    public static void main(String[] args) {
        EditorSubject s = new EditorSubject();
        EditorListener l = new EditorListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("editor:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
