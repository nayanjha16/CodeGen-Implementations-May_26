// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=payments | tier=logging
package org.example.patterns;

public final class PaymentsSingleton {
    private static PaymentsSingleton instance;
    private String value = "default";

    private PaymentsSingleton() {}

    public static synchronized PaymentsSingleton getInstance() {
        if (instance == null) {
            instance = new PaymentsSingleton();
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
