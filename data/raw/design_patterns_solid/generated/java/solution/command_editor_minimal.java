// DesignPatternsSolid | kind=design_pattern | label=command | domain=editor | tier=minimal
package org.example.patterns;

interface EditorCommand {
    String execute();
}

class EditorReceiver {
    public String action(String x) { return "done-editor:" + x; }
}

public class EditorActionCommand implements EditorCommand {
    private final EditorReceiver receiver;
    private final String payload;
    public EditorActionCommand(EditorReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
