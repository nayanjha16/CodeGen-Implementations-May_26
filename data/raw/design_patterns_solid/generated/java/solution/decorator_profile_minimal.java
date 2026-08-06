// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=profile | tier=minimal
package org.example.patterns;

interface ProfileComponent {
    String process(String input);
}

class ProfileCore implements ProfileComponent {
    public String process(String input) { return "profile:" + input; }
}

public class ProfileUpperDecorator implements ProfileComponent {
    private final ProfileComponent inner;
    public ProfileUpperDecorator(ProfileComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
