// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=cart | tier=errors
package org.example.patterns;

import java.util.*;

public class CartMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "cart"; }
}

class CartColleague {
    private final String name;
    private final CartMediator mediator;
    public CartColleague(String name, CartMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
