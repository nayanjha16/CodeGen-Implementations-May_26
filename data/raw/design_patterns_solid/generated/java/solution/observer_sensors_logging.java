// DesignPatternsSolid | kind=design_pattern | label=observer | domain=sensors | tier=logging
package org.example.patterns;

import java.util.*;

interface SensorsObserver {
    void update(String event);
}

public class SensorsSubject {
    private final List<SensorsObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(SensorsObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (SensorsObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class SensorsListener implements SensorsObserver {
    String last = "";
    public void update(String event) { last = "sensors:" + event; }
}
