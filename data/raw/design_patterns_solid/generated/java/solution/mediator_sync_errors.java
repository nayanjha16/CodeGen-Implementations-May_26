// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=sync | tier=errors
package org.example.patterns;

import java.util.*;

public class SyncMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "sync"; }
}

class SyncColleague {
    private final String name;
    private final SyncMediator mediator;
    public SyncColleague(String name, SyncMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
