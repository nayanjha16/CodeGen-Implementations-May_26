// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=audio | tier=logging
package org.example.patterns;

import java.util.*;

public class AudioMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "audio"; }
}

class AudioColleague {
    private final String name;
    private final AudioMediator mediator;
    public AudioColleague(String name, AudioMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
