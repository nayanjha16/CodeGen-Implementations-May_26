// DesignPatternsSolid | kind=design_pattern | label=composite | domain=shipping | tier=logging
package org.example.patterns;

import java.util.*;

interface ShippingNode {
    int size();
}

class ShippingLeaf implements ShippingNode {
    private final int weight;
    public ShippingLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class ShippingComposite implements ShippingNode {
    private final List<ShippingNode> children = new ArrayList<>();
    public void add(ShippingNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (ShippingNode n : children) total += n.size();
        return total;
    }
}
