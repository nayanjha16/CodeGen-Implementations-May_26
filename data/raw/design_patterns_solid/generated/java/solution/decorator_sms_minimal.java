// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=sms | tier=minimal
package org.example.patterns;

interface SmsComponent {
    String process(String input);
}

class SmsCore implements SmsComponent {
    public String process(String input) { return "sms:" + input; }
}

public class SmsUpperDecorator implements SmsComponent {
    private final SmsComponent inner;
    public SmsUpperDecorator(SmsComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
