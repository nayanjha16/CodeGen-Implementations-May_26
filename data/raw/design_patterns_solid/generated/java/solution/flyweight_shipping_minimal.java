// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=shipping | tier=minimal
package org.example.patterns;

import java.util.*;

public class ShippingFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-shipping-" + k);
    }

    public int size() { return cache.size(); }
}
