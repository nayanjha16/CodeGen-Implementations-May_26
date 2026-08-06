// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=payments | tier=errors
package org.example.patterns;

interface PaymentsService {
    String load(String id);
}

class PaymentsRealService implements PaymentsService {
    public String load(String id) { return "real-payments:" + id; }
}

public class PaymentsProxy implements PaymentsService {
    private PaymentsRealService real;
    private final boolean allowed;
    public PaymentsProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new PaymentsRealService();
        return real.load(id);
    }
}
