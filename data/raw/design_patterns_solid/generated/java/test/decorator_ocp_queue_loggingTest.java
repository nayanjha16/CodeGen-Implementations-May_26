package org.example.patterns;
public class QueueDecoratorTest {
    public static void main(String[] args) {
        QueueComponent c = new QueueUpperDecorator(new QueueCore());
        String out = c.process("ab");
        if (!out.equals("QUEUE:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
