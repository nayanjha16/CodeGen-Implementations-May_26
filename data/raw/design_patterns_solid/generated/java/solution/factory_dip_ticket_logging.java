// DesignPatternsSolid | kind=combo | label=factory+dip | domain=ticket | tier=logging
package org.example.patterns;

interface TicketProduct {
    String operate();
}

class TicketBasicProduct implements TicketProduct {
    public String operate() { return "basic-ticket"; }
}

class TicketPremiumProduct implements TicketProduct {
    public String operate() { return "premium-ticket"; }
}

public class TicketFactory {
    public TicketProduct create(String type) {
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new TicketPremiumProduct();
        return new TicketBasicProduct();
    }
}
