// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=backup | tier=logging
package org.example.patterns;

import java.util.*;

public class BackupFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-backup-" + k);
    }

    public int size() { return cache.size(); }
}
