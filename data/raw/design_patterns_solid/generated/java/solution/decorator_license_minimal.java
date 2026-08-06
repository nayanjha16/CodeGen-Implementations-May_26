// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=license | tier=minimal
package org.example.patterns;

interface LicenseComponent {
    String process(String input);
}

class LicenseCore implements LicenseComponent {
    public String process(String input) { return "license:" + input; }
}

public class LicenseUpperDecorator implements LicenseComponent {
    private final LicenseComponent inner;
    public LicenseUpperDecorator(LicenseComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
