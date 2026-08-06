package org.example.patterns;
public class DatabaseDecoratorTest {
    public static void main(String[] args) {
        DatabaseComponent c = new DatabaseUpperDecorator(new DatabaseCore());
        String out = c.process("ab");
        if (!out.equals("DATABASE:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
