// DesignPatternsSolid | kind=design_pattern | label=command | domain=ticket | tier=minimal
package org.example.patterns;

interface TicketCommand {
    String execute();
}

class TicketReceiver {
    public String action(String x) { return "done-ticket:" + x; }
}

public class TicketActionCommand implements TicketCommand {
    private final TicketReceiver receiver;
    private final String payload;
    public TicketActionCommand(TicketReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
