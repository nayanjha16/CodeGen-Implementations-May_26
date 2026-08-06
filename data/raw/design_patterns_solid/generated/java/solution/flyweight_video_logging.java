// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=video | tier=logging
package org.example.patterns;

import java.util.*;

public class VideoFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-video-" + k);
    }

    public int size() { return cache.size(); }
}
