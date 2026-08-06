// DesignPatternsSolid | kind=design_pattern | label=composite | domain=todo | tier=logging
package org.example.patterns;

import java.util.*;

interface TodoNode {
    int size();
}

class TodoLeaf implements TodoNode {
    private final int weight;
    public TodoLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class TodoComposite implements TodoNode {
    private final List<TodoNode> children = new ArrayList<>();
    public void add(TodoNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (TodoNode n : children) total += n.size();
        return total;
    }
}
