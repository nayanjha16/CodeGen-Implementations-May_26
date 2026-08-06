// DesignPatternsSolid | kind=design_pattern | label=composite | domain=backup | tier=minimal
package org.example.patterns;

import java.util.*;

interface BackupNode {
    int size();
}

class BackupLeaf implements BackupNode {
    private final int weight;
    public BackupLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class BackupComposite implements BackupNode {
    private final List<BackupNode> children = new ArrayList<>();
    public void add(BackupNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (BackupNode n : children) total += n.size();
        return total;
    }
}
