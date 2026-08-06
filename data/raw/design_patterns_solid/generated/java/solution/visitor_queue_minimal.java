// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=queue | tier=minimal
package org.example.patterns;

interface QueueVisitor {
    String visitLeaf(QueueLeaf leaf);
}

interface QueueElement {
    String accept(QueueVisitor v);
}

class QueueLeaf implements QueueElement {
    final String name;
    public QueueLeaf(String name) { this.name = name; }
    public String accept(QueueVisitor v) { return v.visitLeaf(this); }
}

public class QueuePrintVisitor implements QueueVisitor {
    public String visitLeaf(QueueLeaf leaf) { return "queue:" + leaf.name; }
}
