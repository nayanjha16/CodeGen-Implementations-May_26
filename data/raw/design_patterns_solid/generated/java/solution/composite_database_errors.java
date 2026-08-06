// DesignPatternsSolid | kind=design_pattern | label=composite | domain=database | tier=errors
package org.example.patterns;

import java.util.*;

interface DatabaseNode {
    int size();
}

class DatabaseLeaf implements DatabaseNode {
    private final int weight;
    public DatabaseLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class DatabaseComposite implements DatabaseNode {
    private final List<DatabaseNode> children = new ArrayList<>();
    public void add(DatabaseNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (DatabaseNode n : children) total += n.size();
        return total;
    }
}
