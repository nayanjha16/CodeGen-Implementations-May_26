// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=map | tier=errors
package org.example.patterns;

interface MapVisitor {
    String visitLeaf(MapLeaf leaf);
}

interface MapElement {
    String accept(MapVisitor v);
}

class MapLeaf implements MapElement {
    final String name;
    public MapLeaf(String name) { this.name = name; }
    public String accept(MapVisitor v) { return v.visitLeaf(this); }
}

public class MapPrintVisitor implements MapVisitor {
    public String visitLeaf(MapLeaf leaf) { return "map:" + leaf.name; }
}
