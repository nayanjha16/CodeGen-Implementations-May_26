// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=analytics | tier=minimal
package org.example.patterns;

interface AnalyticsVisitor {
    String visitLeaf(AnalyticsLeaf leaf);
}

interface AnalyticsElement {
    String accept(AnalyticsVisitor v);
}

class AnalyticsLeaf implements AnalyticsElement {
    final String name;
    public AnalyticsLeaf(String name) { this.name = name; }
    public String accept(AnalyticsVisitor v) { return v.visitLeaf(this); }
}

public class AnalyticsPrintVisitor implements AnalyticsVisitor {
    public String visitLeaf(AnalyticsLeaf leaf) { return "analytics:" + leaf.name; }
}
