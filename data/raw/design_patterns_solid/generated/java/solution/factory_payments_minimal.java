// DesignPatternsSolid | kind=design_pattern | label=factory | domain=payments | tier=minimal
package org.example.patterns;

interface PaymentsProduct {
    String operate();
}

class PaymentsBasicProduct implements PaymentsProduct {
    public String operate() { return "basic-payments"; }
}

class PaymentsPremiumProduct implements PaymentsProduct {
    public String operate() { return "premium-payments"; }
}

public class PaymentsFactory {
    public PaymentsProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new PaymentsPremiumProduct();
        return new PaymentsBasicProduct();
    }
}
