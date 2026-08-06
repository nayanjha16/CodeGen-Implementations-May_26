package org.example.patterns;
public class AnalyticsDecoratorTest {
    public static void main(String[] args) {
        AnalyticsComponent c = new AnalyticsUpperDecorator(new AnalyticsCore());
        String out = c.process("ab");
        if (!out.equals("ANALYTICS:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
