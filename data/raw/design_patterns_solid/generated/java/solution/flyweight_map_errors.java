// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=map | tier=errors
package org.example.patterns;

import java.util.*;

public class MapFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-map-" + k);
    }

    public int size() { return cache.size(); }
}
