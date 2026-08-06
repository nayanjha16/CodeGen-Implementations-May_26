// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=editor | tier=minimal
package org.example.patterns;

interface EditorService {
    String load(String id);
}

class EditorRealService implements EditorService {
    public String load(String id) { return "real-editor:" + id; }
}

public class EditorProxy implements EditorService {
    private EditorRealService real;
    private final boolean allowed;
    public EditorProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new EditorRealService();
        return real.load(id);
    }
}
