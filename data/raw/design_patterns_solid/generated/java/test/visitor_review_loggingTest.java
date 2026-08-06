package org.example.patterns;
public class ReviewVisitorTest {
    public static void main(String[] args) {
        String out = new ReviewLeaf("n").accept(new ReviewPrintVisitor());
        if (!out.equals("review:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
