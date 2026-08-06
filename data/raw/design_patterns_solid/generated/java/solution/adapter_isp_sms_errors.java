// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=sms | tier=errors
package org.example.patterns;

class SmsLegacyApi {
    public String legacyFetch() { return "LEGACY-sms"; }
}

interface SmsTarget {
    String fetch();
}

public class SmsAdapter implements SmsTarget {
    private final SmsLegacyApi legacy;

    public SmsAdapter(SmsLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
