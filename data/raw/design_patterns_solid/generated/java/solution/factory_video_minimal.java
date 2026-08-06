// DesignPatternsSolid | kind=design_pattern | label=factory | domain=video | tier=minimal
package org.example.patterns;

interface VideoProduct {
    String operate();
}

class VideoBasicProduct implements VideoProduct {
    public String operate() { return "basic-video"; }
}

class VideoPremiumProduct implements VideoProduct {
    public String operate() { return "premium-video"; }
}

public class VideoFactory {
    public VideoProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new VideoPremiumProduct();
        return new VideoBasicProduct();
    }
}
