// DesignPatternsSolid | kind=design_pattern | label=observer | domain=cache | tier=minimal
package org.example.patterns;

import java.util.*;

interface CacheObserver {
    void update(String event);
}

public class CacheSubject {
    private final List<CacheObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(CacheObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (CacheObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class CacheListener implements CacheObserver {
    String last = "";
    public void update(String event) { last = "cache:" + event; }
}
