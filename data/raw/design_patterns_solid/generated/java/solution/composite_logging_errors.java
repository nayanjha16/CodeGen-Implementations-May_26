// DesignPatternsSolid | kind=design_pattern | label=composite | domain=logging | tier=errors
package org.example.patterns;

import java.util.*;

interface LoggingNode {
    int size();
}

class LoggingLeaf implements LoggingNode {
    private final int weight;
    public LoggingLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class LoggingComposite implements LoggingNode {
    private final List<LoggingNode> children = new ArrayList<>();
    public void add(LoggingNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (LoggingNode n : children) total += n.size();
        return total;
    }
}
