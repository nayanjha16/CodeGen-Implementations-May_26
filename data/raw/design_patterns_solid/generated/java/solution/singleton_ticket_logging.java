// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=ticket | tier=logging
package org.example.patterns;

public final class TicketSingleton {
    private static TicketSingleton instance;
    private String value = "default";

    private TicketSingleton() {}

    public static synchronized TicketSingleton getInstance() {
        if (instance == null) {
            instance = new TicketSingleton();
        }
        return instance;
    }

    public void setValue(String value) {
        this.value = value;
        System.out.println("[log] set " + value);
    }

    public String getValue() {
        return value;
    }
}
