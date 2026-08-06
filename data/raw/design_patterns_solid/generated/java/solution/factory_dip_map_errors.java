// DesignPatternsSolid | kind=combo | label=factory+dip | domain=map | tier=errors
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
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new MapPremiumProduct();
        return new MapBasicProduct();
    }
}
