// DesignPatternsSolid | kind=design_pattern | label=factory | domain=canvas | tier=logging
package org.example.patterns;

interface CanvasProduct {
    String operate();
}

class CanvasBasicProduct implements CanvasProduct {
    public String operate() { return "basic-canvas"; }
}

class CanvasPremiumProduct implements CanvasProduct {
    public String operate() { return "premium-canvas"; }
}

public class CanvasFactory {
    public CanvasProduct create(String type) {
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new CanvasPremiumProduct();
        return new CanvasBasicProduct();
    }
}
