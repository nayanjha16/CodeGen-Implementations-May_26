// DesignPatternsSolid | kind=design_pattern | label=command | domain=analytics | tier=minimal
package org.example.patterns;

interface AnalyticsCommand {
    String execute();
}

class AnalyticsReceiver {
    public String action(String x) { return "done-analytics:" + x; }
}

public class AnalyticsActionCommand implements AnalyticsCommand {
    private final AnalyticsReceiver receiver;
    private final String payload;
    public AnalyticsActionCommand(AnalyticsReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
