// DesignPatternsSolid | kind=solid | label=dip | domain=config | tier=logging
package org.example.patterns;

// DIP: high-level config module depends on abstraction
interface ConfigGateway {
    String send(String payload);
}

class ConfigHttpGateway implements ConfigGateway {
    public String send(String payload) { return "http-config:" + payload; }
}

public class ConfigAppService {
    private final ConfigGateway gateway;
    public ConfigAppService(ConfigGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
