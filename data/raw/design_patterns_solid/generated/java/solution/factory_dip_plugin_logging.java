// DesignPatternsSolid | kind=combo | label=factory+dip | domain=plugin | tier=logging
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
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new PluginPremiumProduct();
        return new PluginBasicProduct();
    }
}
