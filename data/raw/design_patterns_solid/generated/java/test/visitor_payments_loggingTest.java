package org.example.patterns;
public class PaymentsVisitorTest {
    public static void main(String[] args) {
        String out = new PaymentsLeaf("n").accept(new PaymentsPrintVisitor());
        if (!out.equals("payments:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
