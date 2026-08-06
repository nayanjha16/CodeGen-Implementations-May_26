// DesignPatternsSolid | kind=design_pattern | label=state | domain=todo | tier=errors
package org.example.patterns;

interface TodoState {
    String handle(TodoContext ctx);
}

class TodoOnState implements TodoState {
    public String handle(TodoContext ctx) {
        ctx.setState(new TodoOffState());
        return "was-on-todo";
    }
}

class TodoOffState implements TodoState {
    public String handle(TodoContext ctx) {
        ctx.setState(new TodoOnState());
        return "was-off-todo";
    }
}

public class TodoContext {
    private TodoState state = new TodoOffState();
    public void setState(TodoState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
