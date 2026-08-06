// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=payments | tier=minimal
package org.example.patterns;

interface PaymentsComponent {
    String process(String input);
}

class PaymentsCore implements PaymentsComponent {
    public String process(String input) { return "payments:" + input; }
}

public class PaymentsUpperDecorator implements PaymentsComponent {
    private final PaymentsComponent inner;
    public PaymentsUpperDecorator(PaymentsComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
