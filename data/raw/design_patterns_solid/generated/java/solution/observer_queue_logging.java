// DesignPatternsSolid | kind=design_pattern | label=observer | domain=queue | tier=logging
package org.example.patterns;

import java.util.*;

interface QueueObserver {
    void update(String event);
}

public class QueueSubject {
    private final List<QueueObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(QueueObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (QueueObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class QueueListener implements QueueObserver {
    String last = "";
    public void update(String event) { last = "queue:" + event; }
}
