// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=streaming | tier=minimal
package org.example.patterns;

interface StreamingService {
    String load(String id);
}

class StreamingRealService implements StreamingService {
    public String load(String id) { return "real-streaming:" + id; }
}

public class StreamingProxy implements StreamingService {
    private StreamingRealService real;
    private final boolean allowed;
    public StreamingProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new StreamingRealService();
        return real.load(id);
    }
}
