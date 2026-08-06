// DesignPatternsSolid | kind=design_pattern | label=factory | domain=plugin | tier=errors
package org.example.patterns;

interface PluginProduct {
    String operate();
}

class PluginBasicProduct implements PluginProduct {
    public String operate() { return "basic-plugin"; }
}

class PluginPremiumProduct implements PluginProduct {
    public String operate() { return "premium-plugin"; }
}

public class PluginFactory {
    public PluginProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new PluginPremiumProduct();
        return new PluginBasicProduct();
    }
}
