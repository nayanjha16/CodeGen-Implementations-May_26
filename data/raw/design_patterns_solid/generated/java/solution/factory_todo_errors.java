// DesignPatternsSolid | kind=design_pattern | label=factory | domain=todo | tier=errors
package org.example.patterns;

interface TodoProduct {
    String operate();
}

class TodoBasicProduct implements TodoProduct {
    public String operate() { return "basic-todo"; }
}

class TodoPremiumProduct implements TodoProduct {
    public String operate() { return "premium-todo"; }
}

public class TodoFactory {
    public TodoProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new TodoPremiumProduct();
        return new TodoBasicProduct();
    }
}
