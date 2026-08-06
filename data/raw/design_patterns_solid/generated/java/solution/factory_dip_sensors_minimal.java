// DesignPatternsSolid | kind=combo | label=factory+dip | domain=sensors | tier=minimal
package org.example.patterns;

interface SensorsProduct {
    String operate();
}

class SensorsBasicProduct implements SensorsProduct {
    public String operate() { return "basic-sensors"; }
}

class SensorsPremiumProduct implements SensorsProduct {
    public String operate() { return "premium-sensors"; }
}

public class SensorsFactory {
    public SensorsProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new SensorsPremiumProduct();
        return new SensorsBasicProduct();
    }
}
