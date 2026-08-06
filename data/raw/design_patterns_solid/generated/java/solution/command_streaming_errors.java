// DesignPatternsSolid | kind=design_pattern | label=command | domain=streaming | tier=errors
package org.example.patterns;

interface StreamingCommand {
    String execute();
}

class StreamingReceiver {
    public String action(String x) { return "done-streaming:" + x; }
}

public class StreamingActionCommand implements StreamingCommand {
    private final StreamingReceiver receiver;
    private final String payload;
    public StreamingActionCommand(StreamingReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
