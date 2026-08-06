// DesignPatternsSolid | kind=design_pattern | label=command | domain=shipping | tier=errors
package org.example.patterns;

interface ShippingCommand {
    String execute();
}

class ShippingReceiver {
    public String action(String x) { return "done-shipping:" + x; }
}

public class ShippingActionCommand implements ShippingCommand {
    private final ShippingReceiver receiver;
    private final String payload;
    public ShippingActionCommand(ShippingReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
