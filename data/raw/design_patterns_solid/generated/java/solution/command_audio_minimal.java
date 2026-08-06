// DesignPatternsSolid | kind=design_pattern | label=command | domain=audio | tier=minimal
package org.example.patterns;

interface AudioCommand {
    String execute();
}

class AudioReceiver {
    public String action(String x) { return "done-audio:" + x; }
}

public class AudioActionCommand implements AudioCommand {
    private final AudioReceiver receiver;
    private final String payload;
    public AudioActionCommand(AudioReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
