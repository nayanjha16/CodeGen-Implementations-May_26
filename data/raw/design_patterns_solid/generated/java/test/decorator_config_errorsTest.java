package org.example.patterns;
public class ConfigDecoratorTest {
    public static void main(String[] args) {
        ConfigComponent c = new ConfigUpperDecorator(new ConfigCore());
        String out = c.process("ab");
        if (!out.equals("CONFIG:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
