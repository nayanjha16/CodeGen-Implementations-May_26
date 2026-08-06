package org.example.patterns;
public class NotesStateTest {
    public static void main(String[] args) {
        NotesContext ctx = new NotesContext();
        if (!ctx.request().equals("was-off-notes")) throw new AssertionError();
        if (!ctx.request().equals("was-on-notes")) throw new AssertionError();
        System.out.println("ok");
    }
}
