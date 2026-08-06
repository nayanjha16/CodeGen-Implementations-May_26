// DesignPatternsSolid | kind=design_pattern | label=composite | domain=billing | tier=logging
package org.example.patterns;

import java.util.*;

interface BillingNode {
    int size();
}

class BillingLeaf implements BillingNode {
    private final int weight;
    public BillingLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class BillingComposite implements BillingNode {
    private final List<BillingNode> children = new ArrayList<>();
    public void add(BillingNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (BillingNode n : children) total += n.size();
        return total;
    }
}
