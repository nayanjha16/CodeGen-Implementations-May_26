// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=comment | tier=logging
package org.example.patterns;

interface CommentService {
    String load(String id);
}

class CommentRealService implements CommentService {
    public String load(String id) { return "real-comment:" + id; }
}

public class CommentProxy implements CommentService {
    private CommentRealService real;
    private final boolean allowed;
    public CommentProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new CommentRealService();
        return real.load(id);
    }
}
