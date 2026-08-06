// DesignPatternsSolid | kind=design_pattern | label=factory | domain=map | tier=minimal
package org.example.patterns;

interface MapProduct {
    String operate();
}

class MapBasicProduct implements MapProduct {
    public String operate() { return "basic-map"; }
}

class MapPremiumProduct implements MapProduct {
    public String operate() { return "premium-map"; }
}

public class MapFactory {
    public MapProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new MapPremiumProduct();
        return new MapBasicProduct();
    }
}
