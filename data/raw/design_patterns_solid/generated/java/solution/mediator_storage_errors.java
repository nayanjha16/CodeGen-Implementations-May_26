// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=storage | tier=errors
package org.example.patterns;

import java.util.*;

public class StorageMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "storage"; }
}

class StorageColleague {
    private final String name;
    private final StorageMediator mediator;
    public StorageColleague(String name, StorageMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
