// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=inventory | tier=minimal
package org.example.patterns;

import java.util.*;

public class InventoryFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-inventory-" + k);
    }

    public int size() { return cache.size(); }
}
