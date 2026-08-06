package org.example.patterns;
public class PaymentsDecoratorTest {
    public static void main(String[] args) {
        PaymentsComponent c = new PaymentsUpperDecorator(new PaymentsCore());
        String out = c.process("ab");
        if (!out.equals("PAYMENTS:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
