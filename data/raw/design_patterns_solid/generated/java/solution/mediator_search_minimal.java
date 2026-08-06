// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=search | tier=minimal
package org.example.patterns;

import java.util.*;

public class SearchMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "search"; }
}

class SearchColleague {
    private final String name;
    private final SearchMediator mediator;
    public SearchColleague(String name, SearchMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
