package org.example.patterns;
public class AnalyticsVisitorTest {
    public static void main(String[] args) {
        String out = new AnalyticsLeaf("n").accept(new AnalyticsPrintVisitor());
        if (!out.equals("analytics:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
