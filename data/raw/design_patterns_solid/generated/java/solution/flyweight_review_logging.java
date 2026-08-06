// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=review | tier=logging
package org.example.patterns;

import java.util.*;

public class ReviewFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-review-" + k);
    }

    public int size() { return cache.size(); }
}
