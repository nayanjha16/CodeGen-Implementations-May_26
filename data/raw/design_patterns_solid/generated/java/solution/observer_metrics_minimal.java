// DesignPatternsSolid | kind=design_pattern | label=observer | domain=metrics | tier=minimal
package org.example.patterns;

import java.util.*;

interface MetricsObserver {
    void update(String event);
}

public class MetricsSubject {
    private final List<MetricsObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(MetricsObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (MetricsObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class MetricsListener implements MetricsObserver {
    String last = "";
    public void update(String event) { last = "metrics:" + event; }
}
