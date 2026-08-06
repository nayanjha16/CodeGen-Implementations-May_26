// DesignPatternsSolid | kind=combo | label=factory+dip | domain=sms | tier=errors
package org.example.patterns;

interface SmsProduct {
    String operate();
}

class SmsBasicProduct implements SmsProduct {
    public String operate() { return "basic-sms"; }
}

class SmsPremiumProduct implements SmsProduct {
    public String operate() { return "premium-sms"; }
}

public class SmsFactory {
    public SmsProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new SmsPremiumProduct();
        return new SmsBasicProduct();
    }
}
