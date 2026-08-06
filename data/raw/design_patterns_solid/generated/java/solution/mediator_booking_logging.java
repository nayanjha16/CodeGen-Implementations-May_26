// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=booking | tier=logging
package org.example.patterns;

import java.util.*;

public class BookingMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "booking"; }
}

class BookingColleague {
    private final String name;
    private final BookingMediator mediator;
    public BookingColleague(String name, BookingMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
