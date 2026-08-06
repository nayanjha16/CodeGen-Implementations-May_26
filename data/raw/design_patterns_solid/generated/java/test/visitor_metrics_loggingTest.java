package org.example.patterns;
public class MetricsVisitorTest {
    public static void main(String[] args) {
        String out = new MetricsLeaf("n").accept(new MetricsPrintVisitor());
        if (!out.equals("metrics:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
