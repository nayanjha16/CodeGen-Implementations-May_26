// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=feed | tier=minimal
package org.example.patterns;

interface FeedComponent {
    String process(String input);
}

class FeedCore implements FeedComponent {
    public String process(String input) { return "feed:" + input; }
}

public class FeedUpperDecorator implements FeedComponent {
    private final FeedComponent inner;
    public FeedUpperDecorator(FeedComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
