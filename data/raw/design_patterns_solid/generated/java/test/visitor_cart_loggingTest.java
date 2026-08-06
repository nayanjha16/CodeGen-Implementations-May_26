package org.example.patterns;
public class CartVisitorTest {
    public static void main(String[] args) {
        String out = new CartLeaf("n").accept(new CartPrintVisitor());
        if (!out.equals("cart:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
