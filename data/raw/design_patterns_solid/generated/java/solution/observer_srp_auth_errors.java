// DesignPatternsSolid | kind=combo | label=observer+srp | domain=auth | tier=errors
package org.example.patterns;

import java.util.*;

interface AuthObserver {
    void update(String event);
}

public class AuthSubject {
    private final List<AuthObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(AuthObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (AuthObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class AuthListener implements AuthObserver {
    String last = "";
    public void update(String event) { last = "auth:" + event; }
}
