// DesignPatternsSolid | kind=design_pattern | label=state | domain=notes | tier=logging
package org.example.patterns;

interface NotesState {
    String handle(NotesContext ctx);
}

class NotesOnState implements NotesState {
    public String handle(NotesContext ctx) {
        ctx.setState(new NotesOffState());
        return "was-on-notes";
    }
}

class NotesOffState implements NotesState {
    public String handle(NotesContext ctx) {
        ctx.setState(new NotesOnState());
        return "was-off-notes";
    }
}

public class NotesContext {
    private NotesState state = new NotesOffState();
    public void setState(NotesState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
