// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=audio | tier=logging
package org.example.patterns;

import java.util.*;

public class AudioFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-audio-" + k);
    }

    public int size() { return cache.size(); }
}
