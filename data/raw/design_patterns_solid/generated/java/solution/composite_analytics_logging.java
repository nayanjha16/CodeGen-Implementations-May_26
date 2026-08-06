// DesignPatternsSolid | kind=design_pattern | label=composite | domain=analytics | tier=logging
package org.example.patterns;

import java.util.*;

interface AnalyticsNode {
    int size();
}

class AnalyticsLeaf implements AnalyticsNode {
    private final int weight;
    public AnalyticsLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class AnalyticsComposite implements AnalyticsNode {
    private final List<AnalyticsNode> children = new ArrayList<>();
    public void add(AnalyticsNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (AnalyticsNode n : children) total += n.size();
        return total;
    }
}
