package org.example.patterns;
public class NotesSingletonTest {
    public static void main(String[] args) {
        NotesSingleton a = NotesSingleton.getInstance();
        NotesSingleton b = NotesSingleton.getInstance();
        a.setValue("notes-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("notes-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
