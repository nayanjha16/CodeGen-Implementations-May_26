// DesignPatternsSolid | kind=combo | label=observer+srp | domain=ticket | tier=logging
package org.example.patterns;

import java.util.*;

interface TicketObserver {
    void update(String event);
}

public class TicketSubject {
    private final List<TicketObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(TicketObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (TicketObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class TicketListener implements TicketObserver {
    String last = "";
    public void update(String event) { last = "ticket:" + event; }
}
