// DesignPatternsSolid | kind=combo | label=factory+dip | domain=database | tier=minimal
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
        if ("premium".equalsIgnoreCase(type)) return new DatabasePremiumProduct();
        return new DatabaseBasicProduct();
    }
}
