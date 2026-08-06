// DesignPatternsSolid | kind=design_pattern | label=command | domain=billing | tier=minimal
package org.example.patterns;

interface BillingCommand {
    String execute();
}

class BillingReceiver {
    public String action(String x) { return "done-billing:" + x; }
}

public class BillingActionCommand implements BillingCommand {
    private final BillingReceiver receiver;
    private final String payload;
    public BillingActionCommand(BillingReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
