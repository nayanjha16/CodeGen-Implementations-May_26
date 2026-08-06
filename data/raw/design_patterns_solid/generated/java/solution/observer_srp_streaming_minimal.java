// DesignPatternsSolid | kind=combo | label=observer+srp | domain=streaming | tier=minimal
package org.example.patterns;

import java.util.*;

interface StreamingObserver {
    void update(String event);
}

public class StreamingSubject {
    private final List<StreamingObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(StreamingObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (StreamingObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class StreamingListener implements StreamingObserver {
    String last = "";
    public void update(String event) { last = "streaming:" + event; }
}
