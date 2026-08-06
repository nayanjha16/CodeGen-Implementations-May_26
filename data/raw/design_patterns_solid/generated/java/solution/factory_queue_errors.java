// DesignPatternsSolid | kind=design_pattern | label=factory | domain=queue | tier=errors
package org.example.patterns;

interface QueueProduct {
    String operate();
}

class QueueBasicProduct implements QueueProduct {
    public String operate() { return "basic-queue"; }
}

class QueuePremiumProduct implements QueueProduct {
    public String operate() { return "premium-queue"; }
}

public class QueueFactory {
    public QueueProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new QueuePremiumProduct();
        return new QueueBasicProduct();
    }
}
