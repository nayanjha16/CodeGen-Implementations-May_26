// DesignPatternsSolid | kind=design_pattern | label=observer | domain=audio | tier=errors
package org.example.patterns;

import java.util.*;

interface AudioObserver {
    void update(String event);
}

public class AudioSubject {
    private final List<AudioObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(AudioObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (AudioObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class AudioListener implements AudioObserver {
    String last = "";
    public void update(String event) { last = "audio:" + event; }
}
