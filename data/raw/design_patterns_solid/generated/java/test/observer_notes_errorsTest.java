package org.example.patterns;
public class NotesObserverTest {
    public static void main(String[] args) {
        NotesSubject s = new NotesSubject();
        NotesListener l = new NotesListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("notes:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
