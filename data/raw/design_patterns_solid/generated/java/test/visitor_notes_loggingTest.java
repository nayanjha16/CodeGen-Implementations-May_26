package org.example.patterns;
public class NotesVisitorTest {
    public static void main(String[] args) {
        String out = new NotesLeaf("n").accept(new NotesPrintVisitor());
        if (!out.equals("notes:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
