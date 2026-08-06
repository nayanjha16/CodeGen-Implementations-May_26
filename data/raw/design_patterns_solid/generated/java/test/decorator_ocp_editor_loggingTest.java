package org.example.patterns;
public class EditorDecoratorTest {
    public static void main(String[] args) {
        EditorComponent c = new EditorUpperDecorator(new EditorCore());
        String out = c.process("ab");
        if (!out.equals("EDITOR:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
