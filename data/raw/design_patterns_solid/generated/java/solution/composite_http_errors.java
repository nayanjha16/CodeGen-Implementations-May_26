// DesignPatternsSolid | kind=design_pattern | label=composite | domain=http | tier=errors
package org.example.patterns;

import java.util.*;

interface HttpNode {
    int size();
}

class HttpLeaf implements HttpNode {
    private final int weight;
    public HttpLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class HttpComposite implements HttpNode {
    private final List<HttpNode> children = new ArrayList<>();
    public void add(HttpNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (HttpNode n : children) total += n.size();
        return total;
    }
}
