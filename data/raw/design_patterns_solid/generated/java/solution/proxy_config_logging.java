// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=config | tier=logging
package org.example.patterns;

interface ConfigService {
    String load(String id);
}

class ConfigRealService implements ConfigService {
    public String load(String id) { return "real-config:" + id; }
}

public class ConfigProxy implements ConfigService {
    private ConfigRealService real;
    private final boolean allowed;
    public ConfigProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new ConfigRealService();
        return real.load(id);
    }
}
