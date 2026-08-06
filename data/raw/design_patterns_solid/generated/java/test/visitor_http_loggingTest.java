package org.example.patterns;
public class HttpVisitorTest {
    public static void main(String[] args) {
        String out = new HttpLeaf("n").accept(new HttpPrintVisitor());
        if (!out.equals("http:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
