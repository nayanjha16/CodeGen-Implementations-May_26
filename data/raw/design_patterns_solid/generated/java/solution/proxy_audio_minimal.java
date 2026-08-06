// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=audio | tier=minimal
package org.example.patterns;

interface AudioService {
    String load(String id);
}

class AudioRealService implements AudioService {
    public String load(String id) { return "real-audio:" + id; }
}

public class AudioProxy implements AudioService {
    private AudioRealService real;
    private final boolean allowed;
    public AudioProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new AudioRealService();
        return real.load(id);
    }
}
