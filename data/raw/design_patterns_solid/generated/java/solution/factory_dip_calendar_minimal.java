// DesignPatternsSolid | kind=combo | label=factory+dip | domain=calendar | tier=minimal
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
        if ("premium".equalsIgnoreCase(type)) return new CalendarPremiumProduct();
        return new CalendarBasicProduct();
    }
}
