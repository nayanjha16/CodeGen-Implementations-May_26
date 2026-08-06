package org.example.patterns;
public class CacheDecoratorTest {
    public static void main(String[] args) {
        CacheComponent c = new CacheUpperDecorator(new CacheCore());
        String out = c.process("ab");
        if (!out.equals("CACHE:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
