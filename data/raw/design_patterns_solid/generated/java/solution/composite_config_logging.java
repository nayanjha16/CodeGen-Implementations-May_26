// DesignPatternsSolid | kind=design_pattern | label=composite | domain=config | tier=logging
package org.example.patterns;

import java.util.*;

interface ConfigNode {
    int size();
}

class ConfigLeaf implements ConfigNode {
    private final int weight;
    public ConfigLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class ConfigComposite implements ConfigNode {
    private final List<ConfigNode> children = new ArrayList<>();
    public void add(ConfigNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (ConfigNode n : children) total += n.size();
        return total;
    }
}
