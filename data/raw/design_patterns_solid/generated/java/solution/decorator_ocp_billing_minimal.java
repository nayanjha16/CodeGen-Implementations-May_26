// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=billing | tier=minimal
package org.example.patterns;

interface BillingComponent {
    String process(String input);
}

class BillingCore implements BillingComponent {
    public String process(String input) { return "billing:" + input; }
}

public class BillingUpperDecorator implements BillingComponent {
    private final BillingComponent inner;
    public BillingUpperDecorator(BillingComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
