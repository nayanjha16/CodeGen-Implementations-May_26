// DesignPatternsSolid | kind=design_pattern | label=command | domain=search | tier=errors
package org.example.patterns;

interface SearchCommand {
    String execute();
}

class SearchReceiver {
    public String action(String x) { return "done-search:" + x; }
}

public class SearchActionCommand implements SearchCommand {
    private final SearchReceiver receiver;
    private final String payload;
    public SearchActionCommand(SearchReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
