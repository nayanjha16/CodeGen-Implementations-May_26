// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=search | tier=logging
package org.example.patterns;

interface SearchService {
    String load(String id);
}

class SearchRealService implements SearchService {
    public String load(String id) { return "real-search:" + id; }
}

public class SearchProxy implements SearchService {
    private SearchRealService real;
    private final boolean allowed;
    public SearchProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new SearchRealService();
        return real.load(id);
    }
}
