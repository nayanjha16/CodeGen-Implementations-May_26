// DesignPatternsSolid | kind=design_pattern | label=composite | domain=notifications | tier=minimal
package org.example.patterns;

import java.util.*;

interface NotificationsNode {
    int size();
}

class NotificationsLeaf implements NotificationsNode {
    private final int weight;
    public NotificationsLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class NotificationsComposite implements NotificationsNode {
    private final List<NotificationsNode> children = new ArrayList<>();
    public void add(NotificationsNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (NotificationsNode n : children) total += n.size();
        return total;
    }
}
