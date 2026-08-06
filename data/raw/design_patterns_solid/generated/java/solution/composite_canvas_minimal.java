// DesignPatternsSolid | kind=design_pattern | label=composite | domain=canvas | tier=minimal
package org.example.patterns;

import java.util.*;

interface CanvasNode {
    int size();
}

class CanvasLeaf implements CanvasNode {
    private final int weight;
    public CanvasLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class CanvasComposite implements CanvasNode {
    private final List<CanvasNode> children = new ArrayList<>();
    public void add(CanvasNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (CanvasNode n : children) total += n.size();
        return total;
    }
}
