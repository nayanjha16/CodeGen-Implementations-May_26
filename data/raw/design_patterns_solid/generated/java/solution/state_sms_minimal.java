// DesignPatternsSolid | kind=design_pattern | label=state | domain=sms | tier=minimal
package org.example.patterns;

interface SmsState {
    String handle(SmsContext ctx);
}

class SmsOnState implements SmsState {
    public String handle(SmsContext ctx) {
        ctx.setState(new SmsOffState());
        return "was-on-sms";
    }
}

class SmsOffState implements SmsState {
    public String handle(SmsContext ctx) {
        ctx.setState(new SmsOnState());
        return "was-off-sms";
    }
}

public class SmsContext {
    private SmsState state = new SmsOffState();
    public void setState(SmsState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
