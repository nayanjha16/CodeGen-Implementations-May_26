// DesignPatternsSolid | kind=combo | label=observer+srp | domain=notifications | tier=logging
package org.example.patterns;

import java.util.*;

interface NotificationsObserver {
    void update(String event);
}

public class NotificationsSubject {
    private final List<NotificationsObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(NotificationsObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (NotificationsObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class NotificationsListener implements NotificationsObserver {
    String last = "";
    public void update(String event) { last = "notifications:" + event; }
}
