// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=discount | tier=logging
package org.example.patterns;

interface DiscountService {
    String load(String id);
}

class DiscountRealService implements DiscountService {
    public String load(String id) { return "real-discount:" + id; }
}

public class DiscountProxy implements DiscountService {
    private DiscountRealService real;
    private final boolean allowed;
    public DiscountProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new DiscountRealService();
        return real.load(id);
    }
}
