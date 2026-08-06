// DesignPatternsSolid | kind=design_pattern | label=command | domain=session | tier=errors
package org.example.patterns;

interface SessionCommand {
    String execute();
}

class SessionReceiver {
    public String action(String x) { return "done-session:" + x; }
}

public class SessionActionCommand implements SessionCommand {
    private final SessionReceiver receiver;
    private final String payload;
    public SessionActionCommand(SessionReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
