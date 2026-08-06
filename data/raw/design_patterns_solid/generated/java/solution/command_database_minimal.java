// DesignPatternsSolid | kind=design_pattern | label=command | domain=database | tier=minimal
package org.example.patterns;

interface DatabaseCommand {
    String execute();
}

class DatabaseReceiver {
    public String action(String x) { return "done-database:" + x; }
}

public class DatabaseActionCommand implements DatabaseCommand {
    private final DatabaseReceiver receiver;
    private final String payload;
    public DatabaseActionCommand(DatabaseReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
