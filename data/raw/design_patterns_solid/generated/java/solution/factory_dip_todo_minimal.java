// DesignPatternsSolid | kind=combo | label=factory+dip | domain=todo | tier=minimal
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
        if ("premium".equalsIgnoreCase(type)) return new TodoPremiumProduct();
        return new TodoBasicProduct();
    }
}
