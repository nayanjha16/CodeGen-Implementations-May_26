// DesignPatternsSolid | kind=design_pattern | label=composite | domain=session | tier=minimal
package org.example.patterns;

import java.util.*;

interface SessionNode {
    int size();
}

class SessionLeaf implements SessionNode {
    private final int weight;
    public SessionLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class SessionComposite implements SessionNode {
    private final List<SessionNode> children = new ArrayList<>();
    public void add(SessionNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (SessionNode n : children) total += n.size();
        return total;
    }
}
