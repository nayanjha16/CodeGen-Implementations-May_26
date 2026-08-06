// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=cache | tier=errors
package org.example.patterns;

interface CacheComponent {
    String process(String input);
}

class CacheCore implements CacheComponent {
    public String process(String input) { return "cache:" + input; }
}

public class CacheUpperDecorator implements CacheComponent {
    private final CacheComponent inner;
    public CacheUpperDecorator(CacheComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
