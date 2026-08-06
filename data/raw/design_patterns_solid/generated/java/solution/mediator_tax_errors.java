// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=tax | tier=errors
package org.example.patterns;

import java.util.*;

public class TaxMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "tax"; }
}

class TaxColleague {
    private final String name;
    private final TaxMediator mediator;
    public TaxColleague(String name, TaxMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
