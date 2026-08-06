// DesignPatternsSolid | kind=design_pattern | label=state | domain=booking | tier=minimal
package org.example.patterns;

interface BookingState {
    String handle(BookingContext ctx);
}

class BookingOnState implements BookingState {
    public String handle(BookingContext ctx) {
        ctx.setState(new BookingOffState());
        return "was-on-booking";
    }
}

class BookingOffState implements BookingState {
    public String handle(BookingContext ctx) {
        ctx.setState(new BookingOnState());
        return "was-off-booking";
    }
}

public class BookingContext {
    private BookingState state = new BookingOffState();
    public void setState(BookingState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
