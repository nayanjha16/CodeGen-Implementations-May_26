// DesignPatternsSolid | kind=combo | label=factory+dip | domain=analytics | tier=minimal
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
        if ("premium".equalsIgnoreCase(type)) return new AnalyticsPremiumProduct();
        return new AnalyticsBasicProduct();
    }
}
