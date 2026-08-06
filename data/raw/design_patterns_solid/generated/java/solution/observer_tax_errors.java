// DesignPatternsSolid | kind=design_pattern | label=observer | domain=tax | tier=errors
package org.example.patterns;

import java.util.*;

interface TaxObserver {
    void update(String event);
}

public class TaxSubject {
    private final List<TaxObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(TaxObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (TaxObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class TaxListener implements TaxObserver {
    String last = "";
    public void update(String event) { last = "tax:" + event; }
}
