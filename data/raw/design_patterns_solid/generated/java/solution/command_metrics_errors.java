// DesignPatternsSolid | kind=design_pattern | label=command | domain=metrics | tier=errors
package org.example.patterns;

interface MetricsCommand {
    String execute();
}

class MetricsReceiver {
    public String action(String x) { return "done-metrics:" + x; }
}

public class MetricsActionCommand implements MetricsCommand {
    private final MetricsReceiver receiver;
    private final String payload;
    public MetricsActionCommand(MetricsReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
