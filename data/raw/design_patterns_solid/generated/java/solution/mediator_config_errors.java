// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=config | tier=errors
package org.example.patterns;

import java.util.*;

public class ConfigMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "config"; }
}

class ConfigColleague {
    private final String name;
    private final ConfigMediator mediator;
    public ConfigColleague(String name, ConfigMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
