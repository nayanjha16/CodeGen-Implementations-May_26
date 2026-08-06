// DesignPatternsSolid | kind=combo | label=observer+srp | domain=scheduling | tier=logging
package org.example.patterns;

import java.util.*;

interface SchedulingObserver {
    void update(String event);
}

public class SchedulingSubject {
    private final List<SchedulingObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(SchedulingObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (SchedulingObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class SchedulingListener implements SchedulingObserver {
    String last = "";
    public void update(String event) { last = "scheduling:" + event; }
}
