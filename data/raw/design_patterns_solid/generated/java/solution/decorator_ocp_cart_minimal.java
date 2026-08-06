// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=cart | tier=minimal
package org.example.patterns;

interface CartComponent {
    String process(String input);
}

class CartCore implements CartComponent {
    public String process(String input) { return "cart:" + input; }
}

public class CartUpperDecorator implements CartComponent {
    private final CartComponent inner;
    public CartUpperDecorator(CartComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
