// DesignPatternsSolid | kind=design_pattern | label=command | domain=game | tier=errors
package org.example.patterns;

interface GameCommand {
    String execute();
}

class GameReceiver {
    public String action(String x) { return "done-game:" + x; }
}

public class GameActionCommand implements GameCommand {
    private final GameReceiver receiver;
    private final String payload;
    public GameActionCommand(GameReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
