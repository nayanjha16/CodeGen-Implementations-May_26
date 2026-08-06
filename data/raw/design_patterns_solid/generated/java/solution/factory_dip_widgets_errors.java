// DesignPatternsSolid | kind=combo | label=factory+dip | domain=widgets | tier=errors
package org.example.patterns;

interface WidgetsProduct {
    String operate();
}

class WidgetsBasicProduct implements WidgetsProduct {
    public String operate() { return "basic-widgets"; }
}

class WidgetsPremiumProduct implements WidgetsProduct {
    public String operate() { return "premium-widgets"; }
}

public class WidgetsFactory {
    public WidgetsProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new WidgetsPremiumProduct();
        return new WidgetsBasicProduct();
    }
}
