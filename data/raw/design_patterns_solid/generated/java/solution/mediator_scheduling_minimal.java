// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=scheduling | tier=minimal
package org.example.patterns;

import java.util.*;

public class SchedulingMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "scheduling"; }
}

class SchedulingColleague {
    private final String name;
    private final SchedulingMediator mediator;
    public SchedulingColleague(String name, SchedulingMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
