// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=notes | tier=errors
package org.example.patterns;

interface NotesComponent {
    String process(String input);
}

class NotesCore implements NotesComponent {
    public String process(String input) { return "notes:" + input; }
}

public class NotesUpperDecorator implements NotesComponent {
    private final NotesComponent inner;
    public NotesUpperDecorator(NotesComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
