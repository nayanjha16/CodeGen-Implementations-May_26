// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=http | tier=errors
package org.example.patterns;

interface HttpService {
    String load(String id);
}

class HttpRealService implements HttpService {
    public String load(String id) { return "real-http:" + id; }
}

public class HttpProxy implements HttpService {
    private HttpRealService real;
    private final boolean allowed;
    public HttpProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new HttpRealService();
        return real.load(id);
    }
}
