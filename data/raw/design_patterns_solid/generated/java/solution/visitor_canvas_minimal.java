// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=canvas | tier=minimal
package org.example.patterns;

interface CanvasVisitor {
    String visitLeaf(CanvasLeaf leaf);
}

interface CanvasElement {
    String accept(CanvasVisitor v);
}

class CanvasLeaf implements CanvasElement {
    final String name;
    public CanvasLeaf(String name) { this.name = name; }
    public String accept(CanvasVisitor v) { return v.visitLeaf(this); }
}

public class CanvasPrintVisitor implements CanvasVisitor {
    public String visitLeaf(CanvasLeaf leaf) { return "canvas:" + leaf.name; }
}
