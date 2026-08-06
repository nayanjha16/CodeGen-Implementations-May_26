// DesignPatternsSolid | kind=design_pattern | label=mediator | domain=wallet | tier=minimal
package org.example.patterns;

import java.util.*;

public class WalletMediator {
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {
        log.add(from + "->" + msg);
    }
    public String history() {
        return String.join("|", log);
    }
    public String domain() { return "wallet"; }
}

class WalletColleague {
    private final String name;
    private final WalletMediator mediator;
    public WalletColleague(String name, WalletMediator m) { this.name = name; this.mediator = m; }
    public void send(String msg) { mediator.notify(name, msg); }
}
