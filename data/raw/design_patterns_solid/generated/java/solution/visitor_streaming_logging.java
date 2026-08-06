// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=streaming | tier=logging
package org.example.patterns;

interface StreamingVisitor {
    String visitLeaf(StreamingLeaf leaf);
}

interface StreamingElement {
    String accept(StreamingVisitor v);
}

class StreamingLeaf implements StreamingElement {
    final String name;
    public StreamingLeaf(String name) { this.name = name; }
    public String accept(StreamingVisitor v) { return v.visitLeaf(this); }
}

public class StreamingPrintVisitor implements StreamingVisitor {
    public String visitLeaf(StreamingLeaf leaf) { return "streaming:" + leaf.name; }
}
