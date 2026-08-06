// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=audio | tier=minimal
package org.example.patterns;

interface AudioComponent {
    String process(String input);
}

class AudioCore implements AudioComponent {
    public String process(String input) { return "audio:" + input; }
}

public class AudioUpperDecorator implements AudioComponent {
    private final AudioComponent inner;
    public AudioUpperDecorator(AudioComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
