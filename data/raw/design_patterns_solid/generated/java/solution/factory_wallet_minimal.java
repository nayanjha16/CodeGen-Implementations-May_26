// DesignPatternsSolid | kind=design_pattern | label=factory | domain=wallet | tier=minimal
package org.example.patterns;

interface WalletProduct {
    String operate();
}

class WalletBasicProduct implements WalletProduct {
    public String operate() { return "basic-wallet"; }
}

class WalletPremiumProduct implements WalletProduct {
    public String operate() { return "premium-wallet"; }
}

public class WalletFactory {
    public WalletProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new WalletPremiumProduct();
        return new WalletBasicProduct();
    }
}
