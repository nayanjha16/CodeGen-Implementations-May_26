// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=notifications | tier=errors
package org.example.patterns;

import java.util.*;

public class NotificationsFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-notifications-" + k);
    }

    public int size() { return cache.size(); }
}
