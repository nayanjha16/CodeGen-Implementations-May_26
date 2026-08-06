// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=backup | tier=logging
package org.example.patterns;

interface BackupComponent {
    String process(String input);
}

class BackupCore implements BackupComponent {
    public String process(String input) { return "backup:" + input; }
}

public class BackupUpperDecorator implements BackupComponent {
    private final BackupComponent inner;
    public BackupUpperDecorator(BackupComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
