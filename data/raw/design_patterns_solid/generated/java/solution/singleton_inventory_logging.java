// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=inventory | tier=logging
package org.example.patterns;

public final class InventorySingleton {
    private static InventorySingleton instance;
    private String value = "default";

    private InventorySingleton() {}

    public static synchronized InventorySingleton getInstance() {
        if (instance == null) {
            instance = new InventorySingleton();
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
