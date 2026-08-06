// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=license | tier=logging
package org.example.patterns;

import java.util.*;

public class LicenseFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-license-" + k);
    }

    public int size() { return cache.size(); }
}
