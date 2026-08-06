// DesignPatternsSolid | kind=design_pattern | label=iterator | domain=notes | tier=logging
package org.example.patterns;

import java.util.*;

public class NotesCollection implements Iterable<String> {
    private final List<String> items = new ArrayList<>();
    public void add(String v) { items.add(v); }
    public Iterator<String> iterator() { return items.iterator(); }
    public String join() {
        StringBuilder sb = new StringBuilder("notes");
        for (String it : this) sb.append(":").append(it);
        return sb.toString();
    }
}
