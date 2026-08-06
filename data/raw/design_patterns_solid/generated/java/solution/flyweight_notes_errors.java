// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=notes | tier=errors
package org.example.patterns;

import java.util.*;

public class NotesFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-notes-" + k);
    }

    public int size() { return cache.size(); }
}
