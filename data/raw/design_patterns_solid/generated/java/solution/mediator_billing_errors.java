// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=billing | tier=errors
package org.example.patterns;

import java.util.*;

public class BillingMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "billing"; }
}

class BillingColleague {
    private final String name;
    private final BillingMediator mediator;
    public BillingColleague(String name, BillingMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
