// DesignPatternsSolid | kind=design_pattern | label=factory | domain=audio | tier=errors
package org.example.patterns;

interface AudioProduct {
    String operate();
}

class AudioBasicProduct implements AudioProduct {
    public String operate() { return "basic-audio"; }
}

class AudioPremiumProduct implements AudioProduct {
    public String operate() { return "premium-audio"; }
}

public class AudioFactory {
    public AudioProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new AudioPremiumProduct();
        return new AudioBasicProduct();
    }
}
