// DesignPatternsSolid | kind=solid | label=ocp | domain=audio | tier=minimal
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface AudioDiscount {
    int apply(int price);
}

class AudioNoDiscount implements AudioDiscount {
    public int apply(int price) { return price; }
}

class AudioTenPercent implements AudioDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class AudioPriceEngine {
    private final AudioDiscount discount;
    public AudioPriceEngine(AudioDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "audio"; }
}
