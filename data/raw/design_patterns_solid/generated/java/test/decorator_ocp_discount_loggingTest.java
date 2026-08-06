package org.example.patterns;
public class DiscountDecoratorTest {
    public static void main(String[] args) {
        DiscountComponent c = new DiscountUpperDecorator(new DiscountCore());
        String out = c.process("ab");
        if (!out.equals("DISCOUNT:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
