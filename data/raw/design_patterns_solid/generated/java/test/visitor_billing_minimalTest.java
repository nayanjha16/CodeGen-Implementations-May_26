package org.example.patterns;
public class BillingVisitorTest {
    public static void main(String[] args) {
        String out = new BillingLeaf("n").accept(new BillingPrintVisitor());
        if (!out.equals("billing:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
