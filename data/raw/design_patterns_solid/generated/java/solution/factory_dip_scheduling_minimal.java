// DesignPatternsSolid | kind=combo | label=factory+dip | domain=scheduling | tier=minimal
package org.example.patterns;

interface SchedulingProduct {
    String operate();
}

class SchedulingBasicProduct implements SchedulingProduct {
    public String operate() { return "basic-scheduling"; }
}

class SchedulingPremiumProduct implements SchedulingProduct {
    public String operate() { return "premium-scheduling"; }
}

public class SchedulingFactory {
    public SchedulingProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new SchedulingPremiumProduct();
        return new SchedulingBasicProduct();
    }
}
