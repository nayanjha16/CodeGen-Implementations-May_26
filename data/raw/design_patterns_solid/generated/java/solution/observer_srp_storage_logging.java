// DesignPatternsSolid | kind=combo | label=observer+srp | domain=storage | tier=logging
package org.example.patterns;

import java.util.*;

interface StorageObserver {
    void update(String event);
}

public class StorageSubject {
    private final List<StorageObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(StorageObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (StorageObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class StorageListener implements StorageObserver {
    String last = "";
    public void update(String event) { last = "storage:" + event; }
}
