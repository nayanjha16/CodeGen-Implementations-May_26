// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=sensors | tier=minimal
package org.example.patterns;

interface SensorsVisitor {
    String visitLeaf(SensorsLeaf leaf);
}

interface SensorsElement {
    String accept(SensorsVisitor v);
}

class SensorsLeaf implements SensorsElement {
    final String name;
    public SensorsLeaf(String name) { this.name = name; }
    public String accept(SensorsVisitor v) { return v.visitLeaf(this); }
}

public class SensorsPrintVisitor implements SensorsVisitor {
    public String visitLeaf(SensorsLeaf leaf) { return "sensors:" + leaf.name; }
}
