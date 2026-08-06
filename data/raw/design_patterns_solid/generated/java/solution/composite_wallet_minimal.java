// DesignPatternsSolid | kind=design_pattern | label=composite | domain=wallet | tier=minimal
package org.example.patterns;

import java.util.*;

interface WalletNode {
    int size();
}

class WalletLeaf implements WalletNode {
    private final int weight;
    public WalletLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class WalletComposite implements WalletNode {
    private final List<WalletNode> children = new ArrayList<>();
    public void add(WalletNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (WalletNode n : children) total += n.size();
        return total;
    }
}
