// DesignPatternsSolid | kind=combo | label=factory+dip | domain=logging | tier=logging
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
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new LoggingPremiumProduct();
        return new LoggingBasicProduct();
    }
}
