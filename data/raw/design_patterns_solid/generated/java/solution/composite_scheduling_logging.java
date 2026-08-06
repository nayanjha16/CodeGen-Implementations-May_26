// DesignPatternsSolid | kind=design_pattern | label=composite | domain=scheduling | tier=logging
package org.example.patterns;

import java.util.*;

interface SchedulingNode {
    int size();
}

class SchedulingLeaf implements SchedulingNode {
    private final int weight;
    public SchedulingLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class SchedulingComposite implements SchedulingNode {
    private final List<SchedulingNode> children = new ArrayList<>();
    public void add(SchedulingNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (SchedulingNode n : children) total += n.size();
        return total;
    }
}
