// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=calendar | tier=logging
package org.example.patterns;

import java.util.*;

public class CalendarFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-calendar-" + k);
    }

    public int size() { return cache.size(); }
}
