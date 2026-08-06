// DesignPatternsSolid | kind=design_pattern | label=command | domain=notifications | tier=minimal
package org.example.patterns;

interface NotificationsCommand {
    String execute();
}

class NotificationsReceiver {
    public String action(String x) { return "done-notifications:" + x; }
}

public class NotificationsActionCommand implements NotificationsCommand {
    private final NotificationsReceiver receiver;
    private final String payload;
    public NotificationsActionCommand(NotificationsReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
