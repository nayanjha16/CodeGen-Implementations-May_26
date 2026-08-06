// DesignPatternsSolid | kind=design_pattern | label=observer | domain=map | tier=errors
package org.example.patterns;

import java.util.*;

interface MapObserver {
    void update(String event);
}

public class MapSubject {
    private final List<MapObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(MapObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (MapObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class MapListener implements MapObserver {
    String last = "";
    public void update(String event) { last = "map:" + event; }
}
