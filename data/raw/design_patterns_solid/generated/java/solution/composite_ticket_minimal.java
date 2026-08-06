// DesignPatternsSolid | kind=design_pattern | label=composite | domain=ticket | tier=minimal
package org.example.patterns;

import java.util.*;

interface TicketNode {
    int size();
}

class TicketLeaf implements TicketNode {
    private final int weight;
    public TicketLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class TicketComposite implements TicketNode {
    private final List<TicketNode> children = new ArrayList<>();
    public void add(TicketNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (TicketNode n : children) total += n.size();
        return total;
    }
}
