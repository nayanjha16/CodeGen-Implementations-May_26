// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=sync | tier=logging
package org.example.patterns;

interface SyncComponent {
    String process(String input);
}

class SyncCore implements SyncComponent {
    public String process(String input) { return "sync:" + input; }
}

public class SyncUpperDecorator implements SyncComponent {
    private final SyncComponent inner;
    public SyncUpperDecorator(SyncComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
