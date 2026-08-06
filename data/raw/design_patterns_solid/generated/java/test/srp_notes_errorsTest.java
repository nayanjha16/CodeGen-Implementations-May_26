package org.example.patterns;
public class NotesSrpTest {
    public static void main(String[] args) {
        NotesRecord r = new NotesRecord("a", 3);
        if (!new NotesFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
