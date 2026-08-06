// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=video | tier=logging
package org.example.patterns;

interface VideoComponent {
    String process(String input);
}

class VideoCore implements VideoComponent {
    public String process(String input) { return "video:" + input; }
}

public class VideoUpperDecorator implements VideoComponent {
    private final VideoComponent inner;
    public VideoUpperDecorator(VideoComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
