// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=audio | tier=minimal
package org.example.patterns;

interface AudioStrategy {
    int apply(int amount);
}

class AudioNormalStrategy implements AudioStrategy {
    public int apply(int amount) { return amount; }
}

class AudioDiscountStrategy implements AudioStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class AudioContext {
    private AudioStrategy strategy;
    public AudioContext(AudioStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(AudioStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "audio-strategy"; }
}
