// DesignPatternsSolid | kind=design_pattern | label=observer | domain=calendar | tier=errors
package org.example.patterns;

import java.util.*;

interface CalendarObserver {
    void update(String event);
}

public class CalendarSubject {
    private final List<CalendarObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(CalendarObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (CalendarObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class CalendarListener implements CalendarObserver {
    String last = "";
    public void update(String event) { last = "calendar:" + event; }
}
