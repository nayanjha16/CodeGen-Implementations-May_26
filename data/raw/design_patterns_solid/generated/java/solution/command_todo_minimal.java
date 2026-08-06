// DesignPatternsSolid | kind=design_pattern | label=command | domain=todo | tier=minimal
package org.example.patterns;

interface TodoCommand {
    String execute();
}

class TodoReceiver {
    public String action(String x) { return "done-todo:" + x; }
}

public class TodoActionCommand implements TodoCommand {
    private final TodoReceiver receiver;
    private final String payload;
    public TodoActionCommand(TodoReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
