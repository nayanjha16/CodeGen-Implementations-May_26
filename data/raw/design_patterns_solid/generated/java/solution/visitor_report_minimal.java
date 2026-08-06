// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=report | tier=minimal
package org.example.patterns;

interface ReportVisitor {
    String visitLeaf(ReportLeaf leaf);
}

interface ReportElement {
    String accept(ReportVisitor v);
}

class ReportLeaf implements ReportElement {
    final String name;
    public ReportLeaf(String name) { this.name = name; }
    public String accept(ReportVisitor v) { return v.visitLeaf(this); }
}

public class ReportPrintVisitor implements ReportVisitor {
    public String visitLeaf(ReportLeaf leaf) { return "report:" + leaf.name; }
}
