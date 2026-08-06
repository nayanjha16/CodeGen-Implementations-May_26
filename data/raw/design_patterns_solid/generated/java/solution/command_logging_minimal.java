// DesignPatternsSolid | kind=design_pattern | label=command | domain=logging | tier=minimal
package org.example.patterns;

interface LoggingCommand {
    String execute();
}

class LoggingReceiver {
    public String action(String x) { return "done-logging:" + x; }
}

public class LoggingActionCommand implements LoggingCommand {
    private final LoggingReceiver receiver;
    private final String payload;
    public LoggingActionCommand(LoggingReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
