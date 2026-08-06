// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=tax | tier=errors
package org.example.patterns;

interface TaxComponent {
    String process(String input);
}

class TaxCore implements TaxComponent {
    public String process(String input) { return "tax:" + input; }
}

public class TaxUpperDecorator implements TaxComponent {
    private final TaxComponent inner;
    public TaxUpperDecorator(TaxComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
