// DesignPatternsSolid | kind=design_pattern | label=composite | domain=streaming | tier=minimal
package org.example.patterns;

import java.util.*;

interface StreamingNode {
    int size();
}

class StreamingLeaf implements StreamingNode {
    private final int weight;
    public StreamingLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class StreamingComposite implements StreamingNode {
    private final List<StreamingNode> children = new ArrayList<>();
    public void add(StreamingNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (StreamingNode n : children) total += n.size();
        return total;
    }
}
