package org.example.patterns;
public class CartDecoratorTest {
    public static void main(String[] args) {
        CartComponent c = new CartUpperDecorator(new CartCore());
        String out = c.process("ab");
        if (!out.equals("CART:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
