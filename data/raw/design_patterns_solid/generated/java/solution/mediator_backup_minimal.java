// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=backup | tier=minimal
package org.example.patterns;

import java.util.*;

public class BackupMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "backup"; }
}

class BackupColleague {
    private final String name;
    private final BackupMediator mediator;
    public BackupColleague(String name, BackupMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
