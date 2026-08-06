// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=backup | tier=errors
package org.example.patterns;

interface BackupService {
    String load(String id);
}

class BackupRealService implements BackupService {
    public String load(String id) { return "real-backup:" + id; }
}

public class BackupProxy implements BackupService {
    private BackupRealService real;
    private final boolean allowed;
    public BackupProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new BackupRealService();
        return real.load(id);
    }
}
