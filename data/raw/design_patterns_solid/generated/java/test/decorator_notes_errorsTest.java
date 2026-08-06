package org.example.patterns;
public class NotesDecoratorTest {
    public static void main(String[] args) {
        NotesComponent c = new NotesUpperDecorator(new NotesCore());
        String out = c.process("ab");
        if (!out.equals("NOTES:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
