// DesignPatternsSolid | kind=solid | label=dip | domain=wallet | tier=minimal
package org.example.patterns;

// DIP: high-level wallet module depends on abstraction
interface WalletGateway {
    String send(String payload);
}

class WalletHttpGateway implements WalletGateway {
    public String send(String payload) { return "http-wallet:" + payload; }
}

public class WalletAppService {
    private final WalletGateway gateway;
    public WalletAppService(WalletGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
