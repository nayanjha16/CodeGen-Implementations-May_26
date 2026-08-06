// DesignPatternsSolid | kind=combo | label=observer+srp | domain=profile | tier=minimal
package org.example.patterns;

import java.util.*;

interface ProfileObserver {
    void update(String event);
}

public class ProfileSubject {
    private final List<ProfileObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(ProfileObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (ProfileObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class ProfileListener implements ProfileObserver {
    String last = "";
    public void update(String event) { last = "profile:" + event; }
}
