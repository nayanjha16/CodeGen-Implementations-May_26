// DesignPatternsSolid | kind=combo | label=observer+srp | domain=sync | tier=errors
package org.example.patterns;

import java.util.*;

interface SyncObserver {
    void update(String event);
}

public class SyncSubject {
    private final List<SyncObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(SyncObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (SyncObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class SyncListener implements SyncObserver {
    String last = "";
    public void update(String event) { last = "sync:" + event; }
}
