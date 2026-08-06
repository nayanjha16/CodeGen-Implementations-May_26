// DesignPatternsSolid | kind=design_pattern | label=command | domain=discount | tier=logging
package org.example.patterns;

interface DiscountCommand {
    String execute();
}

class DiscountReceiver {
    public String action(String x) { return "done-discount:" + x; }
}

public class DiscountActionCommand implements DiscountCommand {
    private final DiscountReceiver receiver;
    private final String payload;
    public DiscountActionCommand(DiscountReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
