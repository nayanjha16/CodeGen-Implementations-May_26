// DesignPatternsSolid | kind=design_pattern | label=observer | domain=database | tier=errors
package org.example.patterns;

import java.util.*;

interface DatabaseObserver {
    void update(String event);
}

public class DatabaseSubject {
    private final List<DatabaseObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(DatabaseObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (DatabaseObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class DatabaseListener implements DatabaseObserver {
    String last = "";
    public void update(String event) { last = "database:" + event; }
}
