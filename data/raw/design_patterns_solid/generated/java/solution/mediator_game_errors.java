// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=game | tier=errors
package org.example.patterns;

import java.util.*;

public class GameMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "game"; }
}

class GameColleague {
    private final String name;
    private final GameMediator mediator;
    public GameColleague(String name, GameMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
