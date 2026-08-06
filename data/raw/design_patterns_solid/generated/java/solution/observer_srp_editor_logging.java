// DesignPatternsSolid | kind=combo | label=observer+srp | domain=editor | tier=logging
package org.example.patterns;

import java.util.*;

interface EditorObserver {
    void update(String event);
}

public class EditorSubject {
    private final List<EditorObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(EditorObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (EditorObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class EditorListener implements EditorObserver {
    String last = "";
    public void update(String event) { last = "editor:" + event; }
}
