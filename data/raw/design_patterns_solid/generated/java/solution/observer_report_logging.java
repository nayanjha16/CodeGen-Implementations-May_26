// DesignPatternsSolid | kind=design_pattern | label=observer | domain=report | tier=logging
package org.example.patterns;

import java.util.*;

interface ReportObserver {
    void update(String event);
}

public class ReportSubject {
    private final List<ReportObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(ReportObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (ReportObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class ReportListener implements ReportObserver {
    String last = "";
    public void update(String event) { last = "report:" + event; }
}
