// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=widgets | tier=logging
package org.example.patterns;

import java.util.*;

public class WidgetsFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-widgets-" + k);
    }

    public int size() { return cache.size(); }
}
