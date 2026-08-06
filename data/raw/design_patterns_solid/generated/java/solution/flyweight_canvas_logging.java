// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=canvas | tier=logging
package org.example.patterns;

import java.util.*;

public class CanvasFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-canvas-" + k);
    }

    public int size() { return cache.size(); }
}
