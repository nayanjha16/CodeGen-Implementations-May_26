// DesignPatternsSolid | kind=design_pattern | label=composite | domain=sms | tier=errors
package org.example.patterns;

import java.util.*;

interface SmsNode {
    int size();
}

class SmsLeaf implements SmsNode {
    private final int weight;
    public SmsLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class SmsComposite implements SmsNode {
    private final List<SmsNode> children = new ArrayList<>();
    public void add(SmsNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (SmsNode n : children) total += n.size();
        return total;
    }
}
