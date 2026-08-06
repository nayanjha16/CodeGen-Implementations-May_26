// DesignPatternsSolid | kind=solid | label=isp | domain=wallet | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for wallet
interface WalletReadable {
    String read();
}
interface WalletWritable {
    void write(String v);
}

class WalletStore implements WalletReadable, WalletWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "wallet:" + v; }
}

public class WalletIspClient {
    public static String mirror(WalletReadable r) { return r.read(); }
}
