// DesignPatternsSolid | kind=solid | label=dip | domain=review | tier=minimal
package org.example.patterns;

// DIP: high-level review module depends on abstraction
interface ReviewGateway {
    String send(String payload);
}

class ReviewHttpGateway implements ReviewGateway {
    public String send(String payload) { return "http-review:" + payload; }
}

public class ReviewAppService {
    private final ReviewGateway gateway;
    public ReviewAppService(ReviewGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
