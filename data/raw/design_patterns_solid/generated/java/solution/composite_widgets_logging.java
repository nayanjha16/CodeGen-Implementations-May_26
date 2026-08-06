// DesignPatternsSolid | kind=design_pattern | label=composite | domain=widgets | tier=logging
package org.example.patterns;

import java.util.*;

interface WidgetsNode {
    int size();
}

class WidgetsLeaf implements WidgetsNode {
    private final int weight;
    public WidgetsLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class WidgetsComposite implements WidgetsNode {
    private final List<WidgetsNode> children = new ArrayList<>();
    public void add(WidgetsNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (WidgetsNode n : children) total += n.size();
        return total;
    }
}
