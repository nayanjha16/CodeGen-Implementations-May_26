package org.example.patterns;
public class LoggingDecoratorTest {
    public static void main(String[] args) {
        LoggingComponent c = new LoggingUpperDecorator(new LoggingCore());
        String out = c.process("ab");
        if (!out.equals("LOGGING:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
