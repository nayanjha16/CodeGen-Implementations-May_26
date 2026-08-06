// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=canvas | tier=minimal
package org.example.patterns;

import java.util.*;

public class CanvasMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "canvas"; }
}

class CanvasColleague {
    private final String name;
    private final CanvasMediator mediator;
    public CanvasColleague(String name, CanvasMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
