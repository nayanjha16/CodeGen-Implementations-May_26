// DesignPatternsSolid | kind=design_pattern | label=command | domain=video | tier=logging
package org.example.patterns;

interface VideoCommand {
    String execute();
}

class VideoReceiver {
    public String action(String x) { return "done-video:" + x; }
}

public class VideoActionCommand implements VideoCommand {
    private final VideoReceiver receiver;
    private final String payload;
    public VideoActionCommand(VideoReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
