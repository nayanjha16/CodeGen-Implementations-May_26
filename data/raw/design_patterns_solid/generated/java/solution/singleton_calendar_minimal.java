// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=calendar | tier=minimal
package org.example.patterns;

public final class CalendarSingleton {
    private static CalendarSingleton instance;
    private String value = "default";

    private CalendarSingleton() {}

    public static synchronized CalendarSingleton getInstance() {
        if (instance == null) {
            instance = new CalendarSingleton();
        }
        return instance;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
