// DesignPatternsSolid | kind=combo | label=factory+dip | domain=widgets | tier=logging
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
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new WidgetsPremiumProduct();
        return new WidgetsBasicProduct();
    }
}
