// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=sync | tier=errors
package org.example.patterns;

interface SyncService {
    String load(String id);
}

class SyncRealService implements SyncService {
    public String load(String id) { return "real-sync:" + id; }
}

public class SyncProxy implements SyncService {
    private SyncRealService real;
    private final boolean allowed;
    public SyncProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new SyncRealService();
        return real.load(id);
    }
}
