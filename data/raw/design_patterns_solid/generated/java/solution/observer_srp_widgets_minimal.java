// DesignPatternsSolid | kind=combo | label=observer+srp | domain=widgets | tier=minimal
package org.example.patterns;

import java.util.*;

interface WidgetsObserver {
    void update(String event);
}

public class WidgetsSubject {
    private final List<WidgetsObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(WidgetsObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (WidgetsObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class WidgetsListener implements WidgetsObserver {
    String last = "";
    public void update(String event) { last = "widgets:" + event; }
}
