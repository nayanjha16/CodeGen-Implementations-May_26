// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=license | tier=logging
package org.example.patterns;

interface LicenseService {
    String load(String id);
}

class LicenseRealService implements LicenseService {
    public String load(String id) { return "real-license:" + id; }
}

public class LicenseProxy implements LicenseService {
    private LicenseRealService real;
    private final boolean allowed;
    public LicenseProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new LicenseRealService();
        return real.load(id);
    }
}
