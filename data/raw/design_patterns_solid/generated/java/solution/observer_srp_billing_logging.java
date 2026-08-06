// DesignPatternsSolid | kind=combo | label=observer+srp | domain=billing | tier=logging
package org.example.patterns;

import java.util.*;

interface BillingObserver {
    void update(String event);
}

public class BillingSubject {
    private final List<BillingObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(BillingObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (BillingObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class BillingListener implements BillingObserver {
    String last = "";
    public void update(String event) { last = "billing:" + event; }
}
