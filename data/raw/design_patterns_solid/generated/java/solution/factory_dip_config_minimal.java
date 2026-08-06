// DesignPatternsSolid | kind=combo | label=factory+dip | domain=config | tier=minimal
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
        if ("premium".equalsIgnoreCase(type)) return new ConfigPremiumProduct();
        return new ConfigBasicProduct();
    }
}
