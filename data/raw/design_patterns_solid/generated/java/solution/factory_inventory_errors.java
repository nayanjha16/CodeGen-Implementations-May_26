// DesignPatternsSolid | kind=design_pattern | label=factory | domain=inventory | tier=errors
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
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new InventoryPremiumProduct();
        return new InventoryBasicProduct();
    }
}
