package org.example.patterns;
public class NotesChainTest {
    public static void main(String[] args) {
        NotesHandler h = new NotesLowHandler();
        h.link(new NotesHighHandler());
        if (!h.handle(2, "m").equals("high-notes:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
