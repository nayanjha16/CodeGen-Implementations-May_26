// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=database | tier=minimal
package org.example.patterns;

interface DatabaseComponent {
    String process(String input);
}

class DatabaseCore implements DatabaseComponent {
    public String process(String input) { return "database:" + input; }
}

public class DatabaseUpperDecorator implements DatabaseComponent {
    private final DatabaseComponent inner;
    public DatabaseUpperDecorator(DatabaseComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
