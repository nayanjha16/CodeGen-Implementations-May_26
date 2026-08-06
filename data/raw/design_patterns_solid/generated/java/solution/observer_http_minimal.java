// DesignPatternsSolid | kind=design_pattern | label=observer | domain=http | tier=minimal
package org.example.patterns;

import java.util.*;

interface HttpObserver {
    void update(String event);
}

public class HttpSubject {
    private final List<HttpObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(HttpObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (HttpObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class HttpListener implements HttpObserver {
    String last = "";
    public void update(String event) { last = "http:" + event; }
}
