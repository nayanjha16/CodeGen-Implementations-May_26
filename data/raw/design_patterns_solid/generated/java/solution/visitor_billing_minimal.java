// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=billing | tier=minimal
package org.example.patterns;

interface BillingVisitor {
    String visitLeaf(BillingLeaf leaf);
}

interface BillingElement {
    String accept(BillingVisitor v);
}

class BillingLeaf implements BillingElement {
    final String name;
    public BillingLeaf(String name) { this.name = name; }
    public String accept(BillingVisitor v) { return v.visitLeaf(this); }
}

public class BillingPrintVisitor implements BillingVisitor {
    public String visitLeaf(BillingLeaf leaf) { return "billing:" + leaf.name; }
}
