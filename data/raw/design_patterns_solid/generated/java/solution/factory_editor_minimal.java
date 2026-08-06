// DesignPatternsSolid | kind=design_pattern | label=factory | domain=editor | tier=minimal
package org.example.patterns;

interface EditorProduct {
    String operate();
}

class EditorBasicProduct implements EditorProduct {
    public String operate() { return "basic-editor"; }
}

class EditorPremiumProduct implements EditorProduct {
    public String operate() { return "premium-editor"; }
}

public class EditorFactory {
    public EditorProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new EditorPremiumProduct();
        return new EditorBasicProduct();
    }
}
