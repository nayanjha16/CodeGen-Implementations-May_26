// DesignPatternsSolid | kind=combo | label=factory+dip | domain=logging | tier=errors
package org.example.patterns;

interface LoggingProduct {
    String operate();
}

class LoggingBasicProduct implements LoggingProduct {
    public String operate() { return "basic-logging"; }
}

class LoggingPremiumProduct implements LoggingProduct {
    public String operate() { return "premium-logging"; }
}

public class LoggingFactory {
    public LoggingProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new LoggingPremiumProduct();
        return new LoggingBasicProduct();
    }
}
