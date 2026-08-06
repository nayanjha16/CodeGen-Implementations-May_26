// DesignPatternsSolid | kind=design_pattern | label=observer | domain=backup | tier=errors
package org.example.patterns;

import java.util.*;

interface BackupObserver {
    void update(String event);
}

public class BackupSubject {
    private final List<BackupObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(BackupObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (BackupObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class BackupListener implements BackupObserver {
    String last = "";
    public void update(String event) { last = "backup:" + event; }
}
