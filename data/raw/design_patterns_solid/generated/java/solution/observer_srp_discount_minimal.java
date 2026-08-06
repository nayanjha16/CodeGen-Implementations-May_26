// DesignPatternsSolid | kind=combo | label=observer+srp | domain=discount | tier=minimal
package org.example.patterns;

import java.util.*;

interface DiscountObserver {
    void update(String event);
}

public class DiscountSubject {
    private final List<DiscountObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(DiscountObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (DiscountObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class DiscountListener implements DiscountObserver {
    String last = "";
    public void update(String event) { last = "discount:" + event; }
}
