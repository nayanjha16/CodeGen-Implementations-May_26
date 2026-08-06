package org.example.patterns;
public class CommentVisitorTest {
    public static void main(String[] args) {
        String out = new CommentLeaf("n").accept(new CommentPrintVisitor());
        if (!out.equals("comment:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
