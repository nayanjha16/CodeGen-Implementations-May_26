// DesignPatternsSolid | kind=design_pattern | label=command | domain=feed | tier=logging
package org.example.patterns;

interface FeedCommand {
    String execute();
}

class FeedReceiver {
    public String action(String x) { return "done-feed:" + x; }
}

public class FeedActionCommand implements FeedCommand {
    private final FeedReceiver receiver;
    private final String payload;
    public FeedActionCommand(FeedReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
