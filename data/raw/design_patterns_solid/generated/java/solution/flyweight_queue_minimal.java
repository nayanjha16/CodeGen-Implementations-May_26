// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=queue | tier=minimal
package org.example.patterns;

import java.util.*;

public class QueueFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-queue-" + k);
    }

    public int size() { return cache.size(); }
}
