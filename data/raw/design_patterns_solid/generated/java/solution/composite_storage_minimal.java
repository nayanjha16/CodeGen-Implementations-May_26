// DesignPatternsSolid | kind=design_pattern | label=composite | domain=storage | tier=minimal
package org.example.patterns;

import java.util.*;

interface StorageNode {
    int size();
}

class StorageLeaf implements StorageNode {
    private final int weight;
    public StorageLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class StorageComposite implements StorageNode {
    private final List<StorageNode> children = new ArrayList<>();
    public void add(StorageNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (StorageNode n : children) total += n.size();
        return total;
    }
}
