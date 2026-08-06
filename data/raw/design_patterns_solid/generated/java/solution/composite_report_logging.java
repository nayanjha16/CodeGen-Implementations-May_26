// DesignPatternsSolid | kind=design_pattern | label=composite | domain=report | tier=logging
package org.example.patterns;

import java.util.*;

interface ReportNode {
    int size();
}

class ReportLeaf implements ReportNode {
    private final int weight;
    public ReportLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class ReportComposite implements ReportNode {
    private final List<ReportNode> children = new ArrayList<>();
    public void add(ReportNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (ReportNode n : children) total += n.size();
        return total;
    }
}
