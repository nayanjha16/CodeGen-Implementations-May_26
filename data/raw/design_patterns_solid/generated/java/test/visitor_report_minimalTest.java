package org.example.patterns;
public class ReportVisitorTest {
    public static void main(String[] args) {
        String out = new ReportLeaf("n").accept(new ReportPrintVisitor());
        if (!out.equals("report:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
