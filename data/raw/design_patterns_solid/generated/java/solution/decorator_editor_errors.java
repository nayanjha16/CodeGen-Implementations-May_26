// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=editor | tier=errors
package org.example.patterns;

interface EditorComponent {
    String process(String input);
}

class EditorCore implements EditorComponent {
    public String process(String input) { return "editor:" + input; }
}

public class EditorUpperDecorator implements EditorComponent {
    private final EditorComponent inner;
    public EditorUpperDecorator(EditorComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
