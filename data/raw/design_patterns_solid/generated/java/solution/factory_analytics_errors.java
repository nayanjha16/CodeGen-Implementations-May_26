// DesignPatternsSolid | kind=design_pattern | label=factory | domain=analytics | tier=errors
package org.example.patterns;

interface AnalyticsProduct {
    String operate();
}

class AnalyticsBasicProduct implements AnalyticsProduct {
    public String operate() { return "basic-analytics"; }
}

class AnalyticsPremiumProduct implements AnalyticsProduct {
    public String operate() { return "premium-analytics"; }
}

public class AnalyticsFactory {
    public AnalyticsProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new AnalyticsPremiumProduct();
        return new AnalyticsBasicProduct();
    }
}
