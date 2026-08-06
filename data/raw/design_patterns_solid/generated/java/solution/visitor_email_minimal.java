// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=email | tier=minimal
package org.example.patterns;

interface EmailVisitor {
    String visitLeaf(EmailLeaf leaf);
}

interface EmailElement {
    String accept(EmailVisitor v);
}

class EmailLeaf implements EmailElement {
    final String name;
    public EmailLeaf(String name) { this.name = name; }
    public String accept(EmailVisitor v) { return v.visitLeaf(this); }
}

public class EmailPrintVisitor implements EmailVisitor {
    public String visitLeaf(EmailLeaf leaf) { return "email:" + leaf.name; }
}
