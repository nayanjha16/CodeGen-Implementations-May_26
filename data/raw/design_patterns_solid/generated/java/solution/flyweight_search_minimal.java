// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=search | tier=minimal
package org.example.patterns;

import java.util.*;

public class SearchFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-search-" + k);
    }

    public int size() { return cache.size(); }
}
