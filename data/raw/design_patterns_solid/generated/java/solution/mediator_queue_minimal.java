// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=queue | tier=minimal
package org.example.patterns;

import java.util.*;

public class QueueMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "queue"; }
}

class QueueColleague {
    private final String name;
    private final QueueMediator mediator;
    public QueueColleague(String name, QueueMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
