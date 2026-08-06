// DesignPatternsSolid | kind=design_pattern | label=builder | domain=canvas | tier=errors
package org.example.patterns;

public class CanvasConfig {
    private final String name;
    private final int limit;
    private final boolean enabled;

    private CanvasConfig(Builder b) {
        this.name = b.name;
        this.limit = b.limit;
        this.enabled = b.enabled;
    }

    public String summary() {
        return name + ":" + limit + ":" + enabled;
    }

    public static class Builder {
        private String name = "canvas";
        private int limit = 10;
        private boolean enabled = true;

        public Builder name(String name) {
        if (name == null || name.isEmpty()) throw new IllegalArgumentException("name required");
            this.name = name;
            return this;
        }
        public Builder limit(int limit) { this.limit = limit; return this; }
        public Builder enabled(boolean enabled) { this.enabled = enabled; return this; }
        public CanvasConfig build() { return new CanvasConfig(this); }
    }
}
