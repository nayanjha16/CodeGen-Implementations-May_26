// DesignPatternsSolid | kind=combo | label=observer+srp | domain=canvas | tier=minimal
package org.example.patterns;

import java.util.*;

interface CanvasObserver {
    void update(String event);
}

public class CanvasSubject {
    private final List<CanvasObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(CanvasObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (CanvasObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class CanvasListener implements CanvasObserver {
    String last = "";
    public void update(String event) { last = "canvas:" + event; }
}
