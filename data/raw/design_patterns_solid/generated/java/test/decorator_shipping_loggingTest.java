package org.example.patterns;
public class ShippingDecoratorTest {
    public static void main(String[] args) {
        ShippingComponent c = new ShippingUpperDecorator(new ShippingCore());
        String out = c.process("ab");
        if (!out.equals("SHIPPING:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
