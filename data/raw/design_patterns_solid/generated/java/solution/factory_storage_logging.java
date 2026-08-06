// DesignPatternsSolid | kind=design_pattern | label=factory | domain=storage | tier=logging
package org.example.patterns;

interface StorageProduct {
    String operate();
}

class StorageBasicProduct implements StorageProduct {
    public String operate() { return "basic-storage"; }
}

class StoragePremiumProduct implements StorageProduct {
    public String operate() { return "premium-storage"; }
}

public class StorageFactory {
    public StorageProduct create(String type) {
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new StoragePremiumProduct();
        return new StorageBasicProduct();
    }
}
