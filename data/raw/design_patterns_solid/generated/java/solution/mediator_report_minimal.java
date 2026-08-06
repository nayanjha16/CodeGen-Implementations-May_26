// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=report | tier=minimal
package org.example.patterns;

import java.util.*;

public class ReportMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "report"; }
}

class ReportColleague {
    private final String name;
    private final ReportMediator mediator;
    public ReportColleague(String name, ReportMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
