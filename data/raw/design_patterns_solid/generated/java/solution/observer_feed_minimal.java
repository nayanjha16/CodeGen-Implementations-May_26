// DesignPatternsSolid | kind=design_pattern | label=observer | domain=feed | tier=minimal
package org.example.patterns;

import java.util.*;

interface FeedObserver {
    void update(String event);
}

public class FeedSubject {
    private final List<FeedObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(FeedObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (FeedObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class FeedListener implements FeedObserver {
    String last = "";
    public void update(String event) { last = "feed:" + event; }
}
