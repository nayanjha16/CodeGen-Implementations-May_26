// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=sync | tier=logging
package org.example.patterns;

import java.util.*;

public class SyncFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-sync-" + k);
    }

    public int size() { return cache.size(); }
}
