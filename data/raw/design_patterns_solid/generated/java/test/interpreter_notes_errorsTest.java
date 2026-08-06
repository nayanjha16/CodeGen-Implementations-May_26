package org.example.patterns;
public class NotesInterpreterTest {
    public static void main(String[] args) {
        NotesInterpreter i = new NotesInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
