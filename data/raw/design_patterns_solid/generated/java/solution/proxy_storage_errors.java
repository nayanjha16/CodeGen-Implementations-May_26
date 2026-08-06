// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=storage | tier=errors
package org.example.patterns;

interface StorageService {
    String load(String id);
}

class StorageRealService implements StorageService {
    public String load(String id) { return "real-storage:" + id; }
}

public class StorageProxy implements StorageService {
    private StorageRealService real;
    private final boolean allowed;
    public StorageProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new StorageRealService();
        return real.load(id);
    }
}
