// DesignPatternsSolid | kind=design_pattern | label=command | domain=http | tier=errors
package org.example.patterns;

interface HttpCommand {
    String execute();
}

class HttpReceiver {
    public String action(String x) { return "done-http:" + x; }
}

public class HttpActionCommand implements HttpCommand {
    private final HttpReceiver receiver;
    private final String payload;
    public HttpActionCommand(HttpReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
