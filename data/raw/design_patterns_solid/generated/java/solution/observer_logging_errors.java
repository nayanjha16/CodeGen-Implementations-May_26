// DesignPatternsSolid | kind=design_pattern | label=observer | domain=logging | tier=errors
package org.example.patterns;

import java.util.*;

interface LoggingObserver {
    void update(String event);
}

public class LoggingSubject {
    private final List<LoggingObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(LoggingObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (LoggingObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class LoggingListener implements LoggingObserver {
    String last = "";
    public void update(String event) { last = "logging:" + event; }
}
