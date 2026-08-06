// DesignPatternsSolid | kind=design_pattern | label=command | domain=widgets | tier=errors
package org.example.patterns;

interface WidgetsCommand {
    String execute();
}

class WidgetsReceiver {
    public String action(String x) { return "done-widgets:" + x; }
}

public class WidgetsActionCommand implements WidgetsCommand {
    private final WidgetsReceiver receiver;
    private final String payload;
    public WidgetsActionCommand(WidgetsReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
