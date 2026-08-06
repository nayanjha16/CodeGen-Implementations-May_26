// DesignPatternsSolid | kind=design_pattern | label=factory | domain=backup | tier=minimal
package org.example.patterns;

interface BackupProduct {
    String operate();
}

class BackupBasicProduct implements BackupProduct {
    public String operate() { return "basic-backup"; }
}

class BackupPremiumProduct implements BackupProduct {
    public String operate() { return "premium-backup"; }
}

public class BackupFactory {
    public BackupProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new BackupPremiumProduct();
        return new BackupBasicProduct();
    }
}
