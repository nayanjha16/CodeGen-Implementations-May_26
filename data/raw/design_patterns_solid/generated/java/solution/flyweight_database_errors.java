// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=database | tier=errors
package org.example.patterns;

import java.util.*;

public class DatabaseFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-database-" + k);
    }

    public int size() { return cache.size(); }
}
