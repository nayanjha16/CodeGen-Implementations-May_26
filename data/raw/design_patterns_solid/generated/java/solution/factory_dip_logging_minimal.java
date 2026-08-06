// DesignPatternsSolid | kind=combo | label=factory+dip | domain=logging | tier=minimal
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
        if ("premium".equalsIgnoreCase(type)) return new LoggingPremiumProduct();
        return new LoggingBasicProduct();
    }
}
