// DesignPatternsSolid | kind=solid | label=dip | domain=video | tier=logging
package org.example.patterns;

// DIP: high-level video module depends on abstraction
interface VideoGateway {
    String send(String payload);
}

class VideoHttpGateway implements VideoGateway {
    public String send(String payload) { return "http-video:" + payload; }
}

public class VideoAppService {
    private final VideoGateway gateway;
    public VideoAppService(VideoGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
