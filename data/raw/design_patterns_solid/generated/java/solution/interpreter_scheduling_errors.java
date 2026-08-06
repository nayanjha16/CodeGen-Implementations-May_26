// DesignPatternsSolid | kind=design_pattern | label=interpreter | domain=scheduling | tier=errors
package org.example.patterns;

public class SchedulingInterpreter {
    public int eval(String expr) {
        // tiny language: "n+n" or single int
        if (expr.contains("+")) {
            String[] p = expr.split("\\+");
            return Integer.parseInt(p[0].trim()) + Integer.parseInt(p[1].trim());
        }
        return Integer.parseInt(expr.trim());
    }
    public String tag() { return "scheduling-interp"; }
}
