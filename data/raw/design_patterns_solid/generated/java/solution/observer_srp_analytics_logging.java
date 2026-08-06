// DesignPatternsSolid | kind=combo | label=observer+srp | domain=analytics | tier=logging
package org.example.patterns;

import java.util.*;

interface AnalyticsObserver {
    void update(String event);
}

public class AnalyticsSubject {
    private final List<AnalyticsObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(AnalyticsObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (AnalyticsObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class AnalyticsListener implements AnalyticsObserver {
    String last = "";
    public void update(String event) { last = "analytics:" + event; }
}
