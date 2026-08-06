// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=cart | tier=errors
package org.example.patterns;

interface CartService {
    String load(String id);
}

class CartRealService implements CartService {
    public String load(String id) { return "real-cart:" + id; }
}

public class CartProxy implements CartService {
    private CartRealService real;
    private final boolean allowed;
    public CartProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new CartRealService();
        return real.load(id);
    }
}
