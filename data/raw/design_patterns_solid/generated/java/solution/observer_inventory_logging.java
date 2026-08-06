// DesignPatternsSolid | kind=design_pattern | label=observer | domain=inventory | tier=logging
package org.example.patterns;

import java.util.*;

interface InventoryObserver {
    void update(String event);
}

public class InventorySubject {
    private final List<InventoryObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(InventoryObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (InventoryObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class InventoryListener implements InventoryObserver {
    String last = "";
    public void update(String event) { last = "inventory:" + event; }
}
