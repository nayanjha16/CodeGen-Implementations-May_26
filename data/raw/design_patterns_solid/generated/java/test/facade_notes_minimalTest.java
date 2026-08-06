package org.example.patterns;
public class NotesFacadeTest {
    public static void main(String[] args) {
        NotesFacade f = new NotesFacade();
        if (!f.submit("x").equals("wrote-notes:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
