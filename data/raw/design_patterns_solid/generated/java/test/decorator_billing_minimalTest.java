package org.example.patterns;
public class BillingDecoratorTest {
    public static void main(String[] args) {
        BillingComponent c = new BillingUpperDecorator(new BillingCore());
        String out = c.process("ab");
        if (!out.equals("BILLING:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
