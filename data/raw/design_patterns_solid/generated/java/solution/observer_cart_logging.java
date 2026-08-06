// DesignPatternsSolid | kind=design_pattern | label=observer | domain=cart | tier=logging
package org.example.patterns;

import java.util.*;

interface CartObserver {
    void update(String event);
}

public class CartSubject {
    private final List<CartObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(CartObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (CartObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class CartListener implements CartObserver {
    String last = "";
    public void update(String event) { last = "cart:" + event; }
}
