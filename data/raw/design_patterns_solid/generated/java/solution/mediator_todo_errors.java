// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=todo | tier=errors
package org.example.patterns;

import java.util.*;

public class TodoMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "todo"; }
}

class TodoColleague {
    private final String name;
    private final TodoMediator mediator;
    public TodoColleague(String name, TodoMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
