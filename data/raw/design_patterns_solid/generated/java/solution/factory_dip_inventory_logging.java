// DesignPatternsSolid | kind=combo | label=factory+dip | domain=inventory | tier=logging
package org.example.patterns;

interface InventoryProduct {
    String operate();
}

class InventoryBasicProduct implements InventoryProduct {
    public String operate() { return "basic-inventory"; }
}

class InventoryPremiumProduct implements InventoryProduct {
    public String operate() { return "premium-inventory"; }
}

public class InventoryFactory {
    public InventoryProduct create(String type) {
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new InventoryPremiumProduct();
        return new InventoryBasicProduct();
    }
}
