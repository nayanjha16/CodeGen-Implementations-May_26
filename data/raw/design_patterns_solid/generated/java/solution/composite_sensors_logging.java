// DesignPatternsSolid | kind=design_pattern | label=composite | domain=sensors | tier=logging
package org.example.patterns;

import java.util.*;

interface SensorsNode {
    int size();
}

class SensorsLeaf implements SensorsNode {
    private final int weight;
    public SensorsLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class SensorsComposite implements SensorsNode {
    private final List<SensorsNode> children = new ArrayList<>();
    public void add(SensorsNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (SensorsNode n : children) total += n.size();
        return total;
    }
}
