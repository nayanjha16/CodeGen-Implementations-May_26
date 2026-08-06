// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=report | tier=minimal
package org.example.patterns;

interface ReportService {
    String load(String id);
}

class ReportRealService implements ReportService {
    public String load(String id) { return "real-report:" + id; }
}

public class ReportProxy implements ReportService {
    private ReportRealService real;
    private final boolean allowed;
    public ReportProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new ReportRealService();
        return real.load(id);
    }
}
