package org.example.patterns;
public class MetricsDecoratorTest {
    public static void main(String[] args) {
        MetricsComponent c = new MetricsUpperDecorator(new MetricsCore());
        String out = c.process("ab");
        if (!out.equals("METRICS:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
