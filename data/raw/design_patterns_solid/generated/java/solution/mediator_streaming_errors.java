// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=streaming | tier=errors
package org.example.patterns;

import java.util.*;

public class StreamingMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "streaming"; }
}

class StreamingColleague {
    private final String name;
    private final StreamingMediator mediator;
    public StreamingColleague(String name, StreamingMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
