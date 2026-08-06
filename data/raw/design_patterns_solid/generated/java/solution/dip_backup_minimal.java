// DesignPatternsSolid | kind=solid | label=dip | domain=backup | tier=minimal
package org.example.patterns;

// DIP: high-level backup module depends on abstraction
interface BackupGateway {
    String send(String payload);
}

class BackupHttpGateway implements BackupGateway {
    public String send(String payload) { return "http-backup:" + payload; }
}

public class BackupAppService {
    private final BackupGateway gateway;
    public BackupAppService(BackupGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
