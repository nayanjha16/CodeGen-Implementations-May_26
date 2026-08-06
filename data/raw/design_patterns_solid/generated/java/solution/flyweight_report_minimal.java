// DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=report | tier=minimal
package org.example.patterns;

import java.util.*;

public class ReportFlyweightFactory {
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {
        return cache.computeIfAbsent(key, k -> "fw-report-" + k);
    }

    public int size() { return cache.size(); }
}
