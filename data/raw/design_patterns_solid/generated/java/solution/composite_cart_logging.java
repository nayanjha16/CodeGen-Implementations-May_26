// DesignPatternsSolid | kind=design_pattern | label=composite | domain=cart | tier=logging
package org.example.patterns;

import java.util.*;

interface CartNode {
    int size();
}

class CartLeaf implements CartNode {
    private final int weight;
    public CartLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class CartComposite implements CartNode {
    private final List<CartNode> children = new ArrayList<>();
    public void add(CartNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (CartNode n : children) total += n.size();
        return total;
    }
}
