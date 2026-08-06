// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=comment | tier=minimal
package org.example.patterns;

import java.util.*;

public class CommentMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "comment"; }
}

class CommentColleague {
    private final String name;
    private final CommentMediator mediator;
    public CommentColleague(String name, CommentMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
