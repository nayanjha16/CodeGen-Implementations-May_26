// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=metrics | tier=errors
package org.example.patterns;

import java.util.*;

public class MetricsFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-metrics-" + k);
    }

    public int size() { return cache.size(); }
}
