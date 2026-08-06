// DesignPatternsSolid | kind=design_pattern | label=factory | domain=database | tier=logging
package org.example.patterns;

interface DatabaseProduct {
    String operate();
}

class DatabaseBasicProduct implements DatabaseProduct {
    public String operate() { return "basic-database"; }
}

class DatabasePremiumProduct implements DatabaseProduct {
    public String operate() { return "premium-database"; }
}

public class DatabaseFactory {
    public DatabaseProduct create(String type) {
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new DatabasePremiumProduct();
        return new DatabaseBasicProduct();
    }
}
