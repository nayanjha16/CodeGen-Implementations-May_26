package org.example.patterns;
public class StreamingVisitorTest {
    public static void main(String[] args) {
        String out = new StreamingLeaf("n").accept(new StreamingPrintVisitor());
        if (!out.equals("streaming:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
