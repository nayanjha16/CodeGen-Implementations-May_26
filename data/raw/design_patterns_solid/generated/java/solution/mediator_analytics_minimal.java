// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=analytics | tier=minimal
package org.example.patterns;

import java.util.*;

public class AnalyticsMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "analytics"; }
}

class AnalyticsColleague {
    private final String name;
    private final AnalyticsMediator mediator;
    public AnalyticsColleague(String name, AnalyticsMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
