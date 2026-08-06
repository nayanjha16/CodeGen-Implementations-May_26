// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=license | tier=minimal
package org.example.patterns;

import java.util.*;

public class LicenseMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "license"; }
}

class LicenseColleague {
    private final String name;
    private final LicenseMediator mediator;
    public LicenseColleague(String name, LicenseMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
