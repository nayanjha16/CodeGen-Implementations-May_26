// DesignPatternsSolid | kind=design_pattern | label=command | domain=review | tier=logging
package org.example.patterns;

interface ReviewCommand {
    String execute();
}

class ReviewReceiver {
    public String action(String x) { return "done-review:" + x; }
}

public class ReviewActionCommand implements ReviewCommand {
    private final ReviewReceiver receiver;
    private final String payload;
    public ReviewActionCommand(ReviewReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
