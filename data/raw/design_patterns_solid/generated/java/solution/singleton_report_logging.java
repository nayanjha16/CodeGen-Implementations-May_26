// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=report | tier=logging
package org.example.patterns;

public final class ReportSingleton {
    private static ReportSingleton instance;
    private String value = "default";

    private ReportSingleton() {}

    public static synchronized ReportSingleton getInstance() {
        if (instance == null) {
            instance = new ReportSingleton();
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
