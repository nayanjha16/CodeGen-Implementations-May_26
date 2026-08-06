// DesignPatternsSolid | kind=design_pattern | label=command | domain=backup | tier=errors
package org.example.patterns;

interface BackupCommand {
    String execute();
}

class BackupReceiver {
    public String action(String x) { return "done-backup:" + x; }
}

public class BackupActionCommand implements BackupCommand {
    private final BackupReceiver receiver;
    private final String payload;
    public BackupActionCommand(BackupReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
