package org.example.patterns;
public class NotesMediatorTest {
    public static void main(String[] args) {
        NotesMediator m = new NotesMediator();
        new NotesColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
