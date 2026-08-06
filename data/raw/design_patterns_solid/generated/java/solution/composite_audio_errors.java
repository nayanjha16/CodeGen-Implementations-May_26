// DesignPatternsSolid | kind=design_pattern | label=composite | domain=audio | tier=errors
package org.example.patterns;

import java.util.*;

interface AudioNode {
    int size();
}

class AudioLeaf implements AudioNode {
    private final int weight;
    public AudioLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class AudioComposite implements AudioNode {
    private final List<AudioNode> children = new ArrayList<>();
    public void add(AudioNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (AudioNode n : children) total += n.size();
        return total;
    }
}
