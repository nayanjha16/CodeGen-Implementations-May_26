// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=email | tier=errors
package org.example.patterns;

interface EmailComponent {
    String process(String input);
}

class EmailCore implements EmailComponent {
    public String process(String input) { return "email:" + input; }
}

public class EmailUpperDecorator implements EmailComponent {
    private final EmailComponent inner;
    public EmailUpperDecorator(EmailComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
