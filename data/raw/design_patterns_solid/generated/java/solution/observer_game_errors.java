// DesignPatternsSolid | kind=design_pattern | label=observer | domain=game | tier=errors
package org.example.patterns;

import java.util.*;

interface GameObserver {
    void update(String event);
}

public class GameSubject {
    private final List<GameObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(GameObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (GameObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class GameListener implements GameObserver {
    String last = "";
    public void update(String event) { last = "game:" + event; }
}
