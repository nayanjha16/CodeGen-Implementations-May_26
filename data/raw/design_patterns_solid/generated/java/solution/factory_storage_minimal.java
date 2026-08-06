// DesignPatternsSolid | kind=design_pattern | label=factory | domain=storage | tier=minimal
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
        if ("premium".equalsIgnoreCase(type)) return new StoragePremiumProduct();
        return new StorageBasicProduct();
    }
}
