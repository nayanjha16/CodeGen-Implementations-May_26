// DesignPatternsSolid | kind=design_pattern | label=state | domain=cart | tier=minimal
package org.example.patterns;

interface CartState {
    String handle(CartContext ctx);
}

class CartOnState implements CartState {
    public String handle(CartContext ctx) {
        ctx.setState(new CartOffState());
        return "was-on-cart";
    }
}

class CartOffState implements CartState {
    public String handle(CartContext ctx) {
        ctx.setState(new CartOnState());
        return "was-off-cart";
    }
}

public class CartContext {
    private CartState state = new CartOffState();
    public void setState(CartState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
