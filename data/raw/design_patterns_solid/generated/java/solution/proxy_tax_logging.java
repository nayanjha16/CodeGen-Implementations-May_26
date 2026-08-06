// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=tax | tier=logging
package org.example.patterns;

interface TaxService {
    String load(String id);
}

class TaxRealService implements TaxService {
    public String load(String id) { return "real-tax:" + id; }
}

public class TaxProxy implements TaxService {
    private TaxRealService real;
    private final boolean allowed;
    public TaxProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new TaxRealService();
        return real.load(id);
    }
}
