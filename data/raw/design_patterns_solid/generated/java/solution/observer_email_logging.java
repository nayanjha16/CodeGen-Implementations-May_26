// DesignPatternsSolid | kind=design_pattern | label=observer | domain=email | tier=logging
package org.example.patterns;

import java.util.*;

interface EmailObserver {
    void update(String event);
}

public class EmailSubject {
    private final List<EmailObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(EmailObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (EmailObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class EmailListener implements EmailObserver {
    String last = "";
    public void update(String event) { last = "email:" + event; }
}
