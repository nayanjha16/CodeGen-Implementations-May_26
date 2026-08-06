// DesignPatternsSolid | kind=design_pattern | label=interpreter | domain=feed | tier=minimal
package org.example.patterns;

public class FeedInterpreter {
    public int eval(String expr) {
        // tiny language: "n+n" or single int
        if (expr.contains("+")) {
            String[] p = expr.split("\\+");
            return Integer.parseInt(p[0].trim()) + Integer.parseInt(p[1].trim());
        }
        return Integer.parseInt(expr.trim());
    }
    public String tag() { return "feed-interp"; }
}
