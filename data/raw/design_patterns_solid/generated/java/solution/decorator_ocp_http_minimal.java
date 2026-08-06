// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=http | tier=minimal
package org.example.patterns;

interface HttpComponent {
    String process(String input);
}

class HttpCore implements HttpComponent {
    public String process(String input) { return "http:" + input; }
}

public class HttpUpperDecorator implements HttpComponent {
    private final HttpComponent inner;
    public HttpUpperDecorator(HttpComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
