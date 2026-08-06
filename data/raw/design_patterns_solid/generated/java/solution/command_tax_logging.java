// DesignPatternsSolid | kind=design_pattern | label=command | domain=tax | tier=logging
package org.example.patterns;

interface TaxCommand {
    String execute();
}

class TaxReceiver {
    public String action(String x) { return "done-tax:" + x; }
}

public class TaxActionCommand implements TaxCommand {
    private final TaxReceiver receiver;
    private final String payload;
    public TaxActionCommand(TaxReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
