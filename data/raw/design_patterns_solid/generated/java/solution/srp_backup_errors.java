// DesignPatternsSolid | kind=solid | label=srp | domain=backup | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for backup
class BackupRecord {
    public final String id;
    public final int amount;
    public BackupRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class BackupRepository {
    public String save(BackupRecord r) { return "saved-backup:" + r.id; }
}

public class BackupFormatter {
    public String format(BackupRecord r) { return r.id + "=" + r.amount; }
}
