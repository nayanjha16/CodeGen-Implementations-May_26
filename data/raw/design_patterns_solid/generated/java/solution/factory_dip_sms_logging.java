// DesignPatternsSolid | kind=combo | label=factory+dip | domain=sms | tier=logging
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
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new SmsPremiumProduct();
        return new SmsBasicProduct();
    }
}
