// DesignPatternsSolid | kind=combo | label=factory+dip | domain=config | tier=errors
package org.example.patterns;

interface ConfigProduct {
    String operate();
}

class ConfigBasicProduct implements ConfigProduct {
    public String operate() { return "basic-config"; }
}

class ConfigPremiumProduct implements ConfigProduct {
    public String operate() { return "premium-config"; }
}

public class ConfigFactory {
    public ConfigProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new ConfigPremiumProduct();
        return new ConfigBasicProduct();
    }
}
