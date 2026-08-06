// DesignPatternsSolid | kind=design_pattern | label=composite | domain=queue | tier=minimal
package org.example.patterns;

import java.util.*;

interface QueueNode {
    int size();
}

class QueueLeaf implements QueueNode {
    private final int weight;
    public QueueLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class QueueComposite implements QueueNode {
    private final List<QueueNode> children = new ArrayList<>();
    public void add(QueueNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (QueueNode n : children) total += n.size();
        return total;
    }
}
