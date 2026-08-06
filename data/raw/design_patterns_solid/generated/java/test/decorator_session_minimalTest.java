package org.example.patterns;
public class SessionDecoratorTest {
    public static void main(String[] args) {
        SessionComponent c = new SessionUpperDecorator(new SessionCore());
        String out = c.process("ab");
        if (!out.equals("SESSION:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
