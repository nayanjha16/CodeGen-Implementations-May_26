// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=plugin | tier=logging
package org.example.patterns;

import java.util.*;

public class PluginMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "plugin"; }
}

class PluginColleague {
    private final String name;
    private final PluginMediator mediator;
    public PluginColleague(String name, PluginMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
