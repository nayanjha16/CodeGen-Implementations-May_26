// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=plugin | tier=logging
package org.example.patterns;

interface PluginVisitor {
    String visitLeaf(PluginLeaf leaf);
}

interface PluginElement {
    String accept(PluginVisitor v);
}

class PluginLeaf implements PluginElement {
    final String name;
    public PluginLeaf(String name) { this.name = name; }
    public String accept(PluginVisitor v) { return v.visitLeaf(this); }
}

public class PluginPrintVisitor implements PluginVisitor {
    public String visitLeaf(PluginLeaf leaf) { return "plugin:" + leaf.name; }
}
