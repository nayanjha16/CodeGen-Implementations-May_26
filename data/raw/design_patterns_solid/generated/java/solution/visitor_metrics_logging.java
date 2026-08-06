// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=metrics | tier=logging
package org.example.patterns;

interface MetricsVisitor {
    String visitLeaf(MetricsLeaf leaf);
}

interface MetricsElement {
    String accept(MetricsVisitor v);
}

class MetricsLeaf implements MetricsElement {
    final String name;
    public MetricsLeaf(String name) { this.name = name; }
    public String accept(MetricsVisitor v) { return v.visitLeaf(this); }
}

public class MetricsPrintVisitor implements MetricsVisitor {
    public String visitLeaf(MetricsLeaf leaf) { return "metrics:" + leaf.name; }
}
