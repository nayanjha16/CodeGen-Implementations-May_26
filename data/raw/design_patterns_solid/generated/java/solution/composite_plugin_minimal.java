// DesignPatternsSolid | kind=design_pattern | label=composite | domain=plugin | tier=minimal
package org.example.patterns;

import java.util.*;

interface PluginNode {
    int size();
}

class PluginLeaf implements PluginNode {
    private final int weight;
    public PluginLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class PluginComposite implements PluginNode {
    private final List<PluginNode> children = new ArrayList<>();
    public void add(PluginNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (PluginNode n : children) total += n.size();
        return total;
    }
}
