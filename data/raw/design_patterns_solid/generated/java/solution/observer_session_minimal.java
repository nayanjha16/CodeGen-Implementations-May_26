// DesignPatternsSolid | kind=design_pattern | label=observer | domain=session | tier=minimal
package org.example.patterns;

import java.util.*;

interface SessionObserver {
    void update(String event);
}

public class SessionSubject {
    private final List<SessionObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(SessionObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (SessionObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class SessionListener implements SessionObserver {
    String last = "";
    public void update(String event) { last = "session:" + event; }
}
