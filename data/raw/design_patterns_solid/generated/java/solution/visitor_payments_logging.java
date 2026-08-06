// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=payments | tier=logging
package org.example.patterns;

interface PaymentsVisitor {
    String visitLeaf(PaymentsLeaf leaf);
}

interface PaymentsElement {
    String accept(PaymentsVisitor v);
}

class PaymentsLeaf implements PaymentsElement {
    final String name;
    public PaymentsLeaf(String name) { this.name = name; }
    public String accept(PaymentsVisitor v) { return v.visitLeaf(this); }
}

public class PaymentsPrintVisitor implements PaymentsVisitor {
    public String visitLeaf(PaymentsLeaf leaf) { return "payments:" + leaf.name; }
}
