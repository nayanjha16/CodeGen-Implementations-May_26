// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=comment | tier=minimal
package org.example.patterns;

interface CommentComponent {
    String process(String input);
}

class CommentCore implements CommentComponent {
    public String process(String input) { return "comment:" + input; }
}

public class CommentUpperDecorator implements CommentComponent {
    private final CommentComponent inner;
    public CommentUpperDecorator(CommentComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
