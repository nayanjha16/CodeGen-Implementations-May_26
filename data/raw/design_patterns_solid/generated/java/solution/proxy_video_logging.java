// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=video | tier=logging
package org.example.patterns;

interface VideoService {
    String load(String id);
}

class VideoRealService implements VideoService {
    public String load(String id) { return "real-video:" + id; }
}

public class VideoProxy implements VideoService {
    private VideoRealService real;
    private final boolean allowed;
    public VideoProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new VideoRealService();
        return real.load(id);
    }
}
