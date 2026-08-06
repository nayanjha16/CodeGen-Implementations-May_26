// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=comment | tier=logging
package org.example.patterns;

import java.util.*;

public class CommentFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-comment-" + k);
    }

    public int size() { return cache.size(); }
}
