// DesignPatternsSolid | kind=design_pattern | label=composite | domain=discount | tier=logging
package org.example.patterns;

import java.util.*;

interface DiscountNode {
    int size();
}

class DiscountLeaf implements DiscountNode {
    private final int weight;
    public DiscountLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class DiscountComposite implements DiscountNode {
    private final List<DiscountNode> children = new ArrayList<>();
    public void add(DiscountNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (DiscountNode n : children) total += n.size();
        return total;
    }
}
