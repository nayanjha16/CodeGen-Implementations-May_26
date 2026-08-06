package org.example.patterns;
public class SessionVisitorTest {
    public static void main(String[] args) {
        String out = new SessionLeaf("n").accept(new SessionPrintVisitor());
        if (!out.equals("session:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
