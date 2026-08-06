// DesignPatternsSolid | kind=design_pattern | label=factory | domain=calendar | tier=errors
package org.example.patterns;

interface CalendarProduct {
    String operate();
}

class CalendarBasicProduct implements CalendarProduct {
    public String operate() { return "basic-calendar"; }
}

class CalendarPremiumProduct implements CalendarProduct {
    public String operate() { return "premium-calendar"; }
}

public class CalendarFactory {
    public CalendarProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new CalendarPremiumProduct();
        return new CalendarBasicProduct();
    }
}
