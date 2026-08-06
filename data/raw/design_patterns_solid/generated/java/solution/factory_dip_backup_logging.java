// DesignPatternsSolid | kind=combo | label=factory+dip | domain=backup | tier=logging
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
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new BackupPremiumProduct();
        return new BackupBasicProduct();
    }
}
