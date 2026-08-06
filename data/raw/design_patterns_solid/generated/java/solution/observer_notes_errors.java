// DesignPatternsSolid | kind=design_pattern | label=observer | domain=notes | tier=errors
package org.example.patterns;

import java.util.*;

interface NotesObserver {
    void update(String event);
}

public class NotesSubject {
    private final List<NotesObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(NotesObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (NotesObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class NotesListener implements NotesObserver {
    String last = "";
    public void update(String event) { last = "notes:" + event; }
}
