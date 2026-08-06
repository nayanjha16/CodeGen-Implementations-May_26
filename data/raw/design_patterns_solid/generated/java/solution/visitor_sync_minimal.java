// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=sync | tier=minimal
package org.example.patterns;

interface SyncVisitor {
    String visitLeaf(SyncLeaf leaf);
}

interface SyncElement {
    String accept(SyncVisitor v);
}

class SyncLeaf implements SyncElement {
    final String name;
    public SyncLeaf(String name) { this.name = name; }
    public String accept(SyncVisitor v) { return v.visitLeaf(this); }
}

public class SyncPrintVisitor implements SyncVisitor {
    public String visitLeaf(SyncLeaf leaf) { return "sync:" + leaf.name; }
}
