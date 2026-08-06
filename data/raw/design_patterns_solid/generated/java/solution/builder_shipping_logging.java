// DesignPatternsSolid | kind=design_pattern | label=builder | domain=shipping | tier=logging
package org.example.patterns;

public class ShippingConfig {
    private final String name;
    private final int limit;
    private final boolean enabled;

    private ShippingConfig(Builder b) {
        this.name = b.name;
        this.limit = b.limit;
        this.enabled = b.enabled;
    }

    public String summary() {
        return name + ":" + limit + ":" + enabled;
    }

    public static class Builder {
        private String name = "shipping";
        private int limit = 10;
        private boolean enabled = true;

        public Builder name(String name) {
            this.name = name;
            return this;
        }
        public Builder limit(int limit) { this.limit = limit; return this; }
        public Builder enabled(boolean enabled) { this.enabled = enabled; return this; }
        public ShippingConfig build() { return new ShippingConfig(this); }
    }
}
