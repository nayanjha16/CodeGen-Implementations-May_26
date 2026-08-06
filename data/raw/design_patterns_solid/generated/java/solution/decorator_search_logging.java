// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=search | tier=logging
package org.example.patterns;

interface SearchComponent {
    String process(String input);
}

class SearchCore implements SearchComponent {
    public String process(String input) { return "search:" + input; }
}

public class SearchUpperDecorator implements SearchComponent {
    private final SearchComponent inner;
    public SearchUpperDecorator(SearchComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
