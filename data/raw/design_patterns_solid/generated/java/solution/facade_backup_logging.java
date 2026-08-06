// DesignPatternsSolid | kind=design_pattern | label=facade | domain=backup | tier=logging
package org.example.patterns;

class BackupValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class BackupWriter {
    public String write(String v) { return "wrote-backup:" + v; }
}
public class BackupFacade {
    private final BackupValidator validator = new BackupValidator();
    private final BackupWriter writer = new BackupWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
