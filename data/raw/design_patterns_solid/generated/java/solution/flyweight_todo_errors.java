// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=todo | tier=errors
package org.example.patterns;

import java.util.*;

public class TodoFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-todo-" + k);
    }

    public int size() { return cache.size(); }
}
