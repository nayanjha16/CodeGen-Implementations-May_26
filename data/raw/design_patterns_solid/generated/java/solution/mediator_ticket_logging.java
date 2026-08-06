// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=ticket | tier=logging
package org.example.patterns;

import java.util.*;

public class TicketMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "ticket"; }
}

class TicketColleague {
    private final String name;
    private final TicketMediator mediator;
    public TicketColleague(String name, TicketMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
