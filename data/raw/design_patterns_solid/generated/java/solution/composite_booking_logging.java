// DesignPatternsSolid | kind=design_pattern | label=composite | domain=booking | tier=logging
package org.example.patterns;

import java.util.*;

interface BookingNode {
    int size();
}

class BookingLeaf implements BookingNode {
    private final int weight;
    public BookingLeaf(int weight) { this.weight = weight; }
    public int size() { return weight; }
}

public class BookingComposite implements BookingNode {
    private final List<BookingNode> children = new ArrayList<>();
    public void add(BookingNode n) { children.add(n); }
    public int size() {
        int total = 0;
        for (BookingNode n : children) total += n.size();
        return total;
    }
}
