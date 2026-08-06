// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=discount | tier=logging
package org.example.patterns;

interface DiscountComponent {
    String process(String input);
}

class DiscountCore implements DiscountComponent {
    public String process(String input) { return "discount:" + input; }
}

public class DiscountUpperDecorator implements DiscountComponent {
    private final DiscountComponent inner;
    public DiscountUpperDecorator(DiscountComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
