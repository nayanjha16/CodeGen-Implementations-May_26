// DesignPatternsSolid | kind=combo | label=observer+srp | domain=chat | tier=logging
package org.example.patterns;

import java.util.*;

interface ChatObserver {
    void update(String event);
}

public class ChatSubject {
    private final List<ChatObserver> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach(ChatObserver o) { observers.add(o); }
    public void notifyAllObservers(String event) {
        events.add(event);
        for (ChatObserver o : observers) o.update(event);
    }
    public String last() { return events.isEmpty() ? "" : events.get(events.size()-1); }
}

class ChatListener implements ChatObserver {
    String last = "";
    public void update(String event) { last = "chat:" + event; }
}
