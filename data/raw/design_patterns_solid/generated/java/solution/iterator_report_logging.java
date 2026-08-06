// DesignPatternsSolid | kind=design_pattern | label=iterator | domain=report | tier=logging
package org.example.patterns;

import java.util.*;

public class ReportCollection implements Iterable<String> {
    private final List<String> items = new ArrayList<>();
    public void add(String v) { items.add(v); }
    public Iterator<String> iterator() { return items.iterator(); }
    public String join() {
        StringBuilder sb = new StringBuilder("report");
        for (String it : this) sb.append(":").append(it);
        return sb.toString();
    }
}
