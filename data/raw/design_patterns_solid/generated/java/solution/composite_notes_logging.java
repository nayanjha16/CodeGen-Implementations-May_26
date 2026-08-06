// DesignPatternsSolid | kind=design_pattern | label=composite | domain=notes | tier=logging
package org.example.patterns;

import java.util.*;

interface NotesNode {
    int size();
}

class NotesLeaf implements NotesNode {
    private final int weight;
    public NotesLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class NotesComposite implements NotesNode {
    private final List<NotesNode> children = new ArrayList<>();
    public void add(NotesNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (NotesNode n : children) total += n.size();
        return total;
    }
}
