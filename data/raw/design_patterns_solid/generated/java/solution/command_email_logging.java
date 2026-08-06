// DesignPatternsSolid | kind=design_pattern | label=command | domain=email | tier=logging
package org.example.patterns;

interface EmailCommand {
    String execute();
}

class EmailReceiver {
    public String action(String x) { return "done-email:" + x; }
}

public class EmailActionCommand implements EmailCommand {
    private final EmailReceiver receiver;
    private final String payload;
    public EmailActionCommand(EmailReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
