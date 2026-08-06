// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=plugin | tier=errors
package org.example.patterns;

import java.util.*;

public class PluginFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-plugin-" + k);
    }

    public int size() { return cache.size(); }
}
