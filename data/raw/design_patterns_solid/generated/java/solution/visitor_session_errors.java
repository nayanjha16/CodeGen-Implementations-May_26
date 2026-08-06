// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=session | tier=errors
package org.example.patterns;

interface SessionVisitor {
    String visitLeaf(SessionLeaf leaf);
}

interface SessionElement {
    String accept(SessionVisitor v);
}

class SessionLeaf implements SessionElement {
    final String name;
    public SessionLeaf(String name) { this.name = name; }
    public String accept(SessionVisitor v) { return v.visitLeaf(this); }
}

public class SessionPrintVisitor implements SessionVisitor {
    public String visitLeaf(SessionLeaf leaf) { return "session:" + leaf.name; }
}
