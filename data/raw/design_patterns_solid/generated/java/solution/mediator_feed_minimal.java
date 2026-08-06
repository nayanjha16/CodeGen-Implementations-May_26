// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=feed | tier=minimal
package org.example.patterns;

import java.util.*;

public class FeedMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "feed"; }
}

class FeedColleague {
    private final String name;
    private final FeedMediator mediator;
    public FeedColleague(String name, FeedMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
