// DesignPatternsSolid | kind=design_pattern | label=observer | domain=search | tier=logging
package org.example.patterns;

import java.util.*;

interface SearchObserver {
    void update(String event);
}

public class SearchSubject {
    private final List<SearchObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(SearchObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (SearchObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class SearchListener implements SearchObserver {
    String last = "";
    public void update(String event) { last = "search:" + event; }
}
