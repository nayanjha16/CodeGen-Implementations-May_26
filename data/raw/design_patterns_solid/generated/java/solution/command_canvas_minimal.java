// DesignPatternsSolid | kind=design_pattern | label=command | domain=canvas | tier=minimal
package org.example.patterns;

interface CanvasCommand {
    String execute();
}

class CanvasReceiver {
    public String action(String x) { return "done-canvas:" + x; }
}

public class CanvasActionCommand implements CanvasCommand {
    private final CanvasReceiver receiver;
    private final String payload;
    public CanvasActionCommand(CanvasReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
