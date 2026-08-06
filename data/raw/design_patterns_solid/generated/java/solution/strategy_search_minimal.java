// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=search | tier=minimal
package org.example.patterns;

interface SearchStrategy {
    int apply(int amount);
}

class SearchNormalStrategy implements SearchStrategy {
    public int apply(int amount) { return amount; }
}

class SearchDiscountStrategy implements SearchStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class SearchContext {
    private SearchStrategy strategy;
    public SearchContext(SearchStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(SearchStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "search-strategy"; }
}
