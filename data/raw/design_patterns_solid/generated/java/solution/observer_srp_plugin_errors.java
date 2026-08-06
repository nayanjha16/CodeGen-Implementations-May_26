// DesignPatternsSolid | kind=combo | label=observer+srp | domain=plugin | tier=errors
package org.example.patterns;

import java.util.*;

interface PluginObserver {
    void update(String event);
}

public class PluginSubject {
    private final List<PluginObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(PluginObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (PluginObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class PluginListener implements PluginObserver {
    String last = "";
    public void update(String event) { last = "plugin:" + event; }
}
