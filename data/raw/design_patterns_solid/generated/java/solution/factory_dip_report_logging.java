// DesignPatternsSolid | kind=combo | label=factory+dip | domain=report | tier=logging
package org.example.patterns;

interface ReportProduct {
    String operate();
}

class ReportBasicProduct implements ReportProduct {
    public String operate() { return "basic-report"; }
}

class ReportPremiumProduct implements ReportProduct {
    public String operate() { return "premium-report"; }
}

public class ReportFactory {
    public ReportProduct create(String type) {
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new ReportPremiumProduct();
        return new ReportBasicProduct();
    }
}
