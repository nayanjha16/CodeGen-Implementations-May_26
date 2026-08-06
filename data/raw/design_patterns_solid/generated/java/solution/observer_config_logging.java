// DesignPatternsSolid | kind=design_pattern | label=observer | domain=config | tier=logging
package org.example.patterns;

import java.util.*;

interface ConfigObserver {
    void update(String event);
}

public class ConfigSubject {
    private final List<ConfigObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(ConfigObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (ConfigObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class ConfigListener implements ConfigObserver {
    String last = "";
    public void update(String event) { last = "config:" + event; }
}
