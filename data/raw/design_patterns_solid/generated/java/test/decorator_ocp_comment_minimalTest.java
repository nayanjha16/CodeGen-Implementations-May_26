package org.example.patterns;
public class CommentDecoratorTest {
    public static void main(String[] args) {
        CommentComponent c = new CommentUpperDecorator(new CommentCore());
        String out = c.process("ab");
        if (!out.equals("COMMENT:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
