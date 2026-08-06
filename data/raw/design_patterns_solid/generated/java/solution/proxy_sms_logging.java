// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=sms | tier=logging
package org.example.patterns;

interface SmsService {
    String load(String id);
}

class SmsRealService implements SmsService {
    public String load(String id) { return "real-sms:" + id; }
}

public class SmsProxy implements SmsService {
    private SmsRealService real;
    private final boolean allowed;
    public SmsProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new SmsRealService();
        return real.load(id);
    }
}
