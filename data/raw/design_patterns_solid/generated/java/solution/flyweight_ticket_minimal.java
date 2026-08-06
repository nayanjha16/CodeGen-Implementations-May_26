// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=ticket | tier=minimal
package org.example.patterns;

import java.util.*;

public class TicketFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-ticket-" + k);
    }

    public int size() { return cache.size(); }
}
