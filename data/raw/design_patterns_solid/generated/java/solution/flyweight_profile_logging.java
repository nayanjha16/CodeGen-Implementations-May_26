// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=profile | tier=logging
package org.example.patterns;

import java.util.*;

public class ProfileFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-profile-" + k);
    }

    public int size() { return cache.size(); }
}
