// DesignPatternsSolid | kind=combo | label=factory+dip | domain=license | tier=minimal
package org.example.patterns;

interface LicenseProduct {
    String operate();
}

class LicenseBasicProduct implements LicenseProduct {
    public String operate() { return "basic-license"; }
}

class LicensePremiumProduct implements LicenseProduct {
    public String operate() { return "premium-license"; }
}

public class LicenseFactory {
    public LicenseProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new LicensePremiumProduct();
        return new LicenseBasicProduct();
    }
}
