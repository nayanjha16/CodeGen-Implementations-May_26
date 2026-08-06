// DesignPatternsSolid | kind=design_pattern | label=command | domain=scheduling | tier=minimal
package org.example.patterns;

interface SchedulingCommand {
    String execute();
}

class SchedulingReceiver {
    public String action(String x) { return "done-scheduling:" + x; }
}

public class SchedulingActionCommand implements SchedulingCommand {
    private final SchedulingReceiver receiver;
    private final String payload;
    public SchedulingActionCommand(SchedulingReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
