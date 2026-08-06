// DesignPatternsSolid | kind=design_pattern | label=observer | domain=todo | tier=errors
package org.example.patterns;

import java.util.*;

interface TodoObserver {
    void update(String event);
}

public class TodoSubject {
    private final List<TodoObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(TodoObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (TodoObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class TodoListener implements TodoObserver {
    String last = "";
    public void update(String event) { last = "todo:" + event; }
}
