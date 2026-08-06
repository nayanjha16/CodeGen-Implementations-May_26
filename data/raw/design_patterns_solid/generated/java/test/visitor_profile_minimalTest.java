package org.example.patterns;
public class ProfileVisitorTest {
    public static void main(String[] args) {
        String out = new ProfileLeaf("n").accept(new ProfilePrintVisitor());
        if (!out.equals("profile:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
