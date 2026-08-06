// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=calendar | tier=logging
package org.example.patterns;

import java.util.*;

public class CalendarMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "calendar"; }
}

class CalendarColleague {
    private final String name;
    private final CalendarMediator mediator;
    public CalendarColleague(String name, CalendarMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
