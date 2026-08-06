// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=notifications | tier=errors
package org.example.patterns;

import java.util.*;

public class NotificationsMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "notifications"; }
}

class NotificationsColleague {
    private final String name;
    private final NotificationsMediator mediator;
    public NotificationsColleague(String name, NotificationsMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
