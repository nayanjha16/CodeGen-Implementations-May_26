// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=http | tier=logging
package org.example.patterns;

interface HttpVisitor {
    String visitLeaf(HttpLeaf leaf);
}

interface HttpElement {
    String accept(HttpVisitor v);
}

class HttpLeaf implements HttpElement {
    final String name;
    public HttpLeaf(String name) { this.name = name; }
    public String accept(HttpVisitor v) { return v.visitLeaf(this); }
}

public class HttpPrintVisitor implements HttpVisitor {
    public String visitLeaf(HttpLeaf leaf) { return "http:" + leaf.name; }
}
