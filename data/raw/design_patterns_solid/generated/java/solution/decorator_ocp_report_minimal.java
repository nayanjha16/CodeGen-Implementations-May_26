// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=report | tier=minimal
package org.example.patterns;

interface ReportComponent {
    String process(String input);
}

class ReportCore implements ReportComponent {
    public String process(String input) { return "report:" + input; }
}

public class ReportUpperDecorator implements ReportComponent {
    private final ReportComponent inner;
    public ReportUpperDecorator(ReportComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
