// DesignPatternsSolid | kind=combo | label=factory+dip | domain=queue | tier=logging
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
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new QueuePremiumProduct();
        return new QueueBasicProduct();
    }
}
