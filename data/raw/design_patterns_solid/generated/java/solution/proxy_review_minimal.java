// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=review | tier=minimal
package org.example.patterns;

interface ReviewService {
    String load(String id);
}

class ReviewRealService implements ReviewService {
    public String load(String id) { return "real-review:" + id; }
}

public class ReviewProxy implements ReviewService {
    private ReviewRealService real;
    private final boolean allowed;
    public ReviewProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new ReviewRealService();
        return real.load(id);
    }
}
