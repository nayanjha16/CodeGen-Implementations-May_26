package org.example.patterns;
public class WidgetsDecoratorTest {
    public static void main(String[] args) {
        WidgetsComponent c = new WidgetsUpperDecorator(new WidgetsCore());
        String out = c.process("ab");
        if (!out.equals("WIDGETS:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
