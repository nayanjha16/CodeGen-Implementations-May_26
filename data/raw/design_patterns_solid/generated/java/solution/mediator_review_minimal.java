// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=review | tier=minimal
package org.example.patterns;

import java.util.*;

public class ReviewMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "review"; }
}

class ReviewColleague {
    private final String name;
    private final ReviewMediator mediator;
    public ReviewColleague(String name, ReviewMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
