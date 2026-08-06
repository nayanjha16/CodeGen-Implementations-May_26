// DesignPatternsSolid | kind=design_pattern | label=observer | domain=license | tier=logging
package org.example.patterns;

import java.util.*;

interface LicenseObserver {
    void update(String event);
}

public class LicenseSubject {
    private final List<LicenseObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(LicenseObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (LicenseObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class LicenseListener implements LicenseObserver {
    String last = "";
    public void update(String event) { last = "license:" + event; }
}
