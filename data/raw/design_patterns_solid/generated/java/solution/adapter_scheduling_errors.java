// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=scheduling | tier=errors
package org.example.patterns;

class SchedulingLegacyApi {
    public String legacyFetch() { return "LEGACY-scheduling"; }
}

interface SchedulingTarget {
    String fetch();
}

public class SchedulingAdapter implements SchedulingTarget {
    private final SchedulingLegacyApi legacy;

    public SchedulingAdapter(SchedulingLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
