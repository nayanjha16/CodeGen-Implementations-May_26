package org.example.patterns;
public class EmailDecoratorTest {
    public static void main(String[] args) {
        EmailComponent c = new EmailUpperDecorator(new EmailCore());
        String out = c.process("ab");
        if (!out.equals("EMAIL:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
