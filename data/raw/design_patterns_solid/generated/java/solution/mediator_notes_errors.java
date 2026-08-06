// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=notes | tier=errors
package org.example.patterns;

import java.util.*;

public class NotesMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "notes"; }
}

class NotesColleague {
    private final String name;
    private final NotesMediator mediator;
    public NotesColleague(String name, NotesMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
