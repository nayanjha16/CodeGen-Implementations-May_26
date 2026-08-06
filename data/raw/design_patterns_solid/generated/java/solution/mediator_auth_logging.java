// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=auth | tier=logging
package org.example.patterns;

import java.util.*;

public class AuthMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "auth"; }
}

class AuthColleague {
    private final String name;
    private final AuthMediator mediator;
    public AuthColleague(String name, AuthMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
