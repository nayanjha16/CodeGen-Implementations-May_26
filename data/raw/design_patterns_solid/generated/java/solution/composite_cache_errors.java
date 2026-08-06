// DesignPatternsSolid | kind=design_pattern | label=composite | domain=cache | tier=errors
package org.example.patterns;

import java.util.*;

interface CacheNode {
    int size();
}

class CacheLeaf implements CacheNode {
    private final int weight;
    public CacheLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class CacheComposite implements CacheNode {
    private final List<CacheNode> children = new ArrayList<>();
    public void add(CacheNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (CacheNode n : children) total += n.size();
        return total;
    }
}
