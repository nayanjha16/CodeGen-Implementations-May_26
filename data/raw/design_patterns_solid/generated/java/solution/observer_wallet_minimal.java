// DesignPatternsSolid | kind=design_pattern | label=observer | domain=wallet | tier=minimal
package org.example.patterns;

import java.util.*;

interface WalletObserver {
    void update(String event);
}

public class WalletSubject {
    private final List<WalletObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(WalletObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (WalletObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class WalletListener implements WalletObserver {
    String last = "";
    public void update(String event) { last = "wallet:" + event; }
}
