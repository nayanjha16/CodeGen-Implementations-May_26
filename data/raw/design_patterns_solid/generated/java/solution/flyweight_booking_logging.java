// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=booking | tier=logging
package org.example.patterns;

import java.util.*;

public class BookingFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-booking-" + k);
    }

    public int size() { return cache.size(); }
}
