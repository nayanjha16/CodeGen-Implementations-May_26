package org.example.patterns;
public class SchedulingDecoratorTest {
    public static void main(String[] args) {
        SchedulingComponent c = new SchedulingUpperDecorator(new SchedulingCore());
        String out = c.process("ab");
        if (!out.equals("SCHEDULING:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
