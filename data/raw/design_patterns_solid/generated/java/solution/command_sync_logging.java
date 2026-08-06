// DesignPatternsSolid | kind=design_pattern | label=command | domain=sync | tier=logging
package org.example.patterns;

interface SyncCommand {
    String execute();
}

class SyncReceiver {
    public String action(String x) { return "done-sync:" + x; }
}

public class SyncActionCommand implements SyncCommand {
    private final SyncReceiver receiver;
    private final String payload;
    public SyncActionCommand(SyncReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
