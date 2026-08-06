// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=session | tier=logging
package org.example.patterns;

import java.util.*;

public class SessionMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "session"; }
}

class SessionColleague {
    private final String name;
    private final SessionMediator mediator;
    public SessionColleague(String name, SessionMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
