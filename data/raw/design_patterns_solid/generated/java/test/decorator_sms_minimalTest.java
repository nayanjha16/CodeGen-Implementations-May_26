package org.example.patterns;
public class SmsDecoratorTest {
    public static void main(String[] args) {
        SmsComponent c = new SmsUpperDecorator(new SmsCore());
        String out = c.process("ab");
        if (!out.equals("SMS:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
