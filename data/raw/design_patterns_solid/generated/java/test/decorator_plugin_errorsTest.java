package org.example.patterns;
public class PluginDecoratorTest {
    public static void main(String[] args) {
        PluginComponent c = new PluginUpperDecorator(new PluginCore());
        String out = c.process("ab");
        if (!out.equals("PLUGIN:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
