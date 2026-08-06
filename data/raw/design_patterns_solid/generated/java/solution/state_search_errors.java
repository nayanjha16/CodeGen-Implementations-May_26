// DesignPatternsSolid | kind=design_pattern | label=state | domain=search | tier=errors
package org.example.patterns;

interface SearchState {
    String handle(SearchContext ctx);
}

class SearchOnState implements SearchState {
    public String handle(SearchContext ctx) {
        ctx.setState(new SearchOffState());
        return "was-on-search";
    }
}

class SearchOffState implements SearchState {
    public String handle(SearchContext ctx) {
        ctx.setState(new SearchOnState());
        return "was-off-search";
    }
}

public class SearchContext {
    private SearchState state = new SearchOffState();
    public void setState(SearchState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
