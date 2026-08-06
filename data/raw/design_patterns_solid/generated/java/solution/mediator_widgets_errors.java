// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=widgets | tier=errors
package org.example.patterns;

import java.util.*;

public class WidgetsMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "widgets"; }
}

class WidgetsColleague {
    private final String name;
    private final WidgetsMediator mediator;
    public WidgetsColleague(String name, WidgetsMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
