// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=review | tier=logging
package org.example.patterns;

interface ReviewVisitor {
    String visitLeaf(ReviewLeaf leaf);
}

interface ReviewElement {
    String accept(ReviewVisitor v);
}

class ReviewLeaf implements ReviewElement {
    final String name;
    public ReviewLeaf(String name) { this.name = name; }
    public String accept(ReviewVisitor v) { return v.visitLeaf(this); }
}

public class ReviewPrintVisitor implements ReviewVisitor {
    public String visitLeaf(ReviewLeaf leaf) { return "review:" + leaf.name; }
}
