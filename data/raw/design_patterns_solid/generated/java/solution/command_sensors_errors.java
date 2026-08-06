// DesignPatternsSolid | kind=design_pattern | label=command | domain=sensors | tier=errors
package org.example.patterns;

interface SensorsCommand {
    String execute();
}

class SensorsReceiver {
    public String action(String x) { return "done-sensors:" + x; }
}

public class SensorsActionCommand implements SensorsCommand {
    private final SensorsReceiver receiver;
    private final String payload;
    public SensorsActionCommand(SensorsReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
