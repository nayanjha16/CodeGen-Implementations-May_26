// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=report | tier=logging
package org.example.patterns;

interface ReportStrategy {
    int apply(int amount);
}

class ReportNormalStrategy implements ReportStrategy {
    public int apply(int amount) { return amount; }
}

class ReportDiscountStrategy implements ReportStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class ReportContext {
    private ReportStrategy strategy;
    public ReportContext(ReportStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(ReportStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "report-strategy"; }
}
