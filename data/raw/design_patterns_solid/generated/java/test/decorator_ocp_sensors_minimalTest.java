package org.example.patterns;
public class SensorsDecoratorTest {
    public static void main(String[] args) {
        SensorsComponent c = new SensorsUpperDecorator(new SensorsCore());
        String out = c.process("ab");
        if (!out.equals("SENSORS:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
