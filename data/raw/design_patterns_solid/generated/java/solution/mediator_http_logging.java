// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=http | tier=logging
package org.example.patterns;

import java.util.*;

public class HttpMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "http"; }
}

class HttpColleague {
    private final String name;
    private final HttpMediator mediator;
    public HttpColleague(String name, HttpMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
