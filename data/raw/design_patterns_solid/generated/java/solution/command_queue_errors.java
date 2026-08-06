// DesignPatternsSolid | kind=design_pattern | label=command | domain=queue | tier=errors
package org.example.patterns;

interface QueueCommand {
    String execute();
}

class QueueReceiver {
    public String action(String x) { return "done-queue:" + x; }
}

public class QueueActionCommand implements QueueCommand {
    private final QueueReceiver receiver;
    private final String payload;
    public QueueActionCommand(QueueReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
