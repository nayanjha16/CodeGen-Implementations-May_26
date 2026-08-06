// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=sensors | tier=errors
package org.example.patterns;

import java.util.*;

public class SensorsMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "sensors"; }
}

class SensorsColleague {
    private final String name;
    private final SensorsMediator mediator;
    public SensorsColleague(String name, SensorsMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
