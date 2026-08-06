// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=comment | tier=logging
package org.example.patterns;

interface CommentVisitor {
    String visitLeaf(CommentLeaf leaf);
}

interface CommentElement {
    String accept(CommentVisitor v);
}

class CommentLeaf implements CommentElement {
    final String name;
    public CommentLeaf(String name) { this.name = name; }
    public String accept(CommentVisitor v) { return v.visitLeaf(this); }
}

public class CommentPrintVisitor implements CommentVisitor {
    public String visitLeaf(CommentLeaf leaf) { return "comment:" + leaf.name; }
}
