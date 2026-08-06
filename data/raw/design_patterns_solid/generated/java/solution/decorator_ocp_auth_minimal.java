// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=auth | tier=minimal
package org.example.patterns;

interface AuthComponent {
    String process(String input);
}

class AuthCore implements AuthComponent {
    public String process(String input) { return "auth:" + input; }
}

public class AuthUpperDecorator implements AuthComponent {
    private final AuthComponent inner;
    public AuthUpperDecorator(AuthComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
