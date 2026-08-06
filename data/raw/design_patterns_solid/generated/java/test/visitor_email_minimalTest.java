package org.example.patterns;
public class EmailVisitorTest {
    public static void main(String[] args) {
        String out = new EmailLeaf("n").accept(new EmailPrintVisitor());
        if (!out.equals("email:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
