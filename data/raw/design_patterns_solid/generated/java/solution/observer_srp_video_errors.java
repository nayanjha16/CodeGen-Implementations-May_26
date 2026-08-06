// DesignPatternsSolid | kind=combo | label=observer+srp | domain=video | tier=errors
package org.example.patterns;

import java.util.*;

interface VideoObserver {
    void update(String event);
}

public class VideoSubject {
    private final List<VideoObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(VideoObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (VideoObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class VideoListener implements VideoObserver {
    String last = "";
    public void update(String event) { last = "video:" + event; }
}
