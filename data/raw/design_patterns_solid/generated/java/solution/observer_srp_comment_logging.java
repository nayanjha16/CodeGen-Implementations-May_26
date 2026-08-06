// DesignPatternsSolid | kind=combo | label=observer+srp | domain=comment | tier=logging
package org.example.patterns;

import java.util.*;

interface CommentObserver {
    void update(String event);
}

public class CommentSubject {
    private final List<CommentObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(CommentObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (CommentObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class CommentListener implements CommentObserver {
    String last = "";
    public void update(String event) { last = "comment:" + event; }
}
