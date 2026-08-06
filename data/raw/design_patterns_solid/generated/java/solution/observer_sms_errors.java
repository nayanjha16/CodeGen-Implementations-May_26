// DesignPatternsSolid | kind=design_pattern | label=observer | domain=sms | tier=errors
package org.example.patterns;

import java.util.*;

interface SmsObserver {
    void update(String event);
}

public class SmsSubject {
    private final List<SmsObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(SmsObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (SmsObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class SmsListener implements SmsObserver {
    String last = "";
    public void update(String event) { last = "sms:" + event; }
}
