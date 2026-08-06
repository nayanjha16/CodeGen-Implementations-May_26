// DesignPatternsSolid | kind=design_pattern | label=command | domain=notes | tier=logging
package org.example.patterns;

interface NotesCommand {
    String execute();
}

class NotesReceiver {
    public String action(String x) { return "done-notes:" + x; }
}

public class NotesActionCommand implements NotesCommand {
    private final NotesReceiver receiver;
    private final String payload;
    public NotesActionCommand(NotesReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
