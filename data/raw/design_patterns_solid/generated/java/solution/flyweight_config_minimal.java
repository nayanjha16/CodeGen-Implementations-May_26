// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=config | tier=minimal
package org.example.patterns;

import java.util.*;

public class ConfigFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-config-" + k);
    }

    public int size() { return cache.size(); }
}
