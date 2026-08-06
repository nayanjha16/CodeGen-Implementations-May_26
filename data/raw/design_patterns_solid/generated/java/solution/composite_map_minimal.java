// DesignPatternsSolid | kind=design_pattern | label=composite | domain=map | tier=minimal
package org.example.patterns;

import java.util.*;

interface MapNode {
    int size();
}

class MapLeaf implements MapNode {
    private final int weight;
    public MapLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class MapComposite implements MapNode {
    private final List<MapNode> children = new ArrayList<>();
    public void add(MapNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (MapNode n : children) total += n.size();
        return total;
    }
}
