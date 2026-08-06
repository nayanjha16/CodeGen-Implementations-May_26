// DesignPatternsSolid | kind=design_pattern | label=composite | domain=chat | tier=minimal
package org.example.patterns;

import java.util.*;

interface ChatNode {
    int size();
}

class ChatLeaf implements ChatNode {
    private final int weight;
    public ChatLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class ChatComposite implements ChatNode {
    private final List<ChatNode> children = new ArrayList<>();
    public void add(ChatNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (ChatNode n : children) total += n.size();
        return total;
    }
}
