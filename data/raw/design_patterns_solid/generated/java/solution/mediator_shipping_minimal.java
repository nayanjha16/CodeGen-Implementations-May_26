// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=shipping | tier=minimal
package org.example.patterns;

import java.util.*;

public class ShippingMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "shipping"; }
}

class ShippingColleague {
    private final String name;
    private final ShippingMediator mediator;
    public ShippingColleague(String name, ShippingMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
