// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=logging | tier=minimal
package org.example.patterns;

import java.util.*;

public class LoggingMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "logging"; }
}

class LoggingColleague {
    private final String name;
    private final LoggingMediator mediator;
    public LoggingColleague(String name, LoggingMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
