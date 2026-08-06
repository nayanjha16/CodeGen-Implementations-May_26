// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=todo | tier=logging
package org.example.patterns;

interface TodoComponent {
    String process(String input);
}

class TodoCore implements TodoComponent {
    public String process(String input) { return "todo:" + input; }
}

public class TodoUpperDecorator implements TodoComponent {
    private final TodoComponent inner;
    public TodoUpperDecorator(TodoComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
