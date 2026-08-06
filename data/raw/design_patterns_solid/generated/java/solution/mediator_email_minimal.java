// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=email | tier=minimal
package org.example.patterns;

import java.util.*;

public class EmailMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "email"; }
}

class EmailColleague {
    private final String name;
    private final EmailMediator mediator;
    public EmailColleague(String name, EmailMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
