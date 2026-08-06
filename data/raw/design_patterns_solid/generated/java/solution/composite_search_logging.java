// DesignPatternsSolid | kind=design_pattern | label=composite | domain=search | tier=logging
package org.example.patterns;

import java.util.*;

interface SearchNode {
    int size();
}

class SearchLeaf implements SearchNode {
    private final int weight;
    public SearchLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class SearchComposite implements SearchNode {
    private final List<SearchNode> children = new ArrayList<>();
    public void add(SearchNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (SearchNode n : children) total += n.size();
        return total;
    }
}
