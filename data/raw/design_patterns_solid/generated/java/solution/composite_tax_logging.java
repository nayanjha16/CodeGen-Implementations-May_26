// DesignPatternsSolid | kind=design_pattern | label=composite | domain=tax | tier=logging
package org.example.patterns;

import java.util.*;

interface TaxNode {
    int size();
}

class TaxLeaf implements TaxNode {
    private final int weight;
    public TaxLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class TaxComposite implements TaxNode {
    private final List<TaxNode> children = new ArrayList<>();
    public void add(TaxNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (TaxNode n : children) total += n.size();
        return total;
    }
}
