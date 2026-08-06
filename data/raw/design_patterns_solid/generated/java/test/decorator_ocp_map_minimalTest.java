package org.example.patterns;
public class MapDecoratorTest {
    public static void main(String[] args) {
        MapComponent c = new MapUpperDecorator(new MapCore());
        String out = c.process("ab");
        if (!out.equals("MAP:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
