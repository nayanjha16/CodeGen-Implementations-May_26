// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=sms | tier=logging
package org.example.patterns;

public final class SmsSingleton {
    private static SmsSingleton instance;
    private String value = "default";

    private SmsSingleton() {}

    public static synchronized SmsSingleton getInstance() {
        if (instance == null) {
            instance = new SmsSingleton();
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
