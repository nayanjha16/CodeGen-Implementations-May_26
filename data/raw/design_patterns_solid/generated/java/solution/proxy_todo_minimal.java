// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=todo | tier=minimal
package org.example.patterns;

interface TodoService {
    String load(String id);
}

class TodoRealService implements TodoService {
    public String load(String id) { return "real-todo:" + id; }
}

public class TodoProxy implements TodoService {
    private TodoRealService real;
    private final boolean allowed;
    public TodoProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new TodoRealService();
        return real.load(id);
    }
}
