package org.example.patterns;
public class LoggingVisitorTest {
    public static void main(String[] args) {
        String out = new LoggingLeaf("n").accept(new LoggingPrintVisitor());
        if (!out.equals("logging:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
