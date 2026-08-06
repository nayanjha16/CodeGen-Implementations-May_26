package org.example.patterns;
public class HttpDecoratorTest {
    public static void main(String[] args) {
        HttpComponent c = new HttpUpperDecorator(new HttpCore());
        String out = c.process("ab");
        if (!out.equals("HTTP:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
