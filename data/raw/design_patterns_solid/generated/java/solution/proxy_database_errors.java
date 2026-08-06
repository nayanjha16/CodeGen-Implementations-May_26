// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=database | tier=errors
package org.example.patterns;

interface DatabaseService {
    String load(String id);
}

class DatabaseRealService implements DatabaseService {
    public String load(String id) { return "real-database:" + id; }
}

public class DatabaseProxy implements DatabaseService {
    private DatabaseRealService real;
    private final boolean allowed;
    public DatabaseProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new DatabaseRealService();
        return real.load(id);
    }
}
