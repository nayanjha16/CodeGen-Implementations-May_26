// DesignPatternsSolid | kind=combo | label=factory+dip | domain=booking | tier=minimal
package org.example.patterns;

interface BookingProduct {
    String operate();
}

class BookingBasicProduct implements BookingProduct {
    public String operate() { return "basic-booking"; }
}

class BookingPremiumProduct implements BookingProduct {
    public String operate() { return "premium-booking"; }
}

public class BookingFactory {
    public BookingProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new BookingPremiumProduct();
        return new BookingBasicProduct();
    }
}
