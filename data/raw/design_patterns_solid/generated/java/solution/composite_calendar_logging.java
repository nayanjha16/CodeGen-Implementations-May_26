// DesignPatternsSolid | kind=design_pattern | label=composite | domain=calendar | tier=logging
package org.example.patterns;

import java.util.*;

interface CalendarNode {
    int size();
}

class CalendarLeaf implements CalendarNode {
    private final int weight;
    public CalendarLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class CalendarComposite implements CalendarNode {
    private final List<CalendarNode> children = new ArrayList<>();
    public void add(CalendarNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (CalendarNode n : children) total += n.size();
        return total;
    }
}
