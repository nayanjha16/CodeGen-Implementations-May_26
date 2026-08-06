// DesignPatternsSolid | kind=design_pattern | label=composite | domain=game | tier=logging
package org.example.patterns;

import java.util.*;

interface GameNode {
    int size();
}

class GameLeaf implements GameNode {
    private final int weight;
    public GameLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class GameComposite implements GameNode {
    private final List<GameNode> children = new ArrayList<>();
    public void add(GameNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (GameNode n : children) total += n.size();
        return total;
    }
}
