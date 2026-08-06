// DesignPatternsSolid | kind=combo | label=factory+dip | domain=metrics | tier=minimal
package org.example.patterns;

interface MetricsProduct {
    String operate();
}

class MetricsBasicProduct implements MetricsProduct {
    public String operate() { return "basic-metrics"; }
}

class MetricsPremiumProduct implements MetricsProduct {
    public String operate() { return "premium-metrics"; }
}

public class MetricsFactory {
    public MetricsProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new MetricsPremiumProduct();
        return new MetricsBasicProduct();
    }
}
