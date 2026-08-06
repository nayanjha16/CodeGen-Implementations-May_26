// DesignPatternsSolid | kind=design_pattern | label=iterator | domain=auth | tier=logging
package org.example.patterns;

import java.util.*;

public class AuthCollection implements Iterable<String> {
    private final List<String> items = new ArrayList<>();
    public void add(String v) { items.add(v); }
    public Iterator<String> iterator() { return items.iterator(); }
    public String join() {
        StringBuilder sb = new StringBuilder("auth");
        for (String it : this) sb.append(":").append(it);
        return sb.toString();
    }
}
