// DesignPatternsSolid | kind=combo | label=factory+dip | domain=streaming | tier=errors
package org.example.patterns;

interface StreamingProduct {
    String operate();
}

class StreamingBasicProduct implements StreamingProduct {
    public String operate() { return "basic-streaming"; }
}

class StreamingPremiumProduct implements StreamingProduct {
    public String operate() { return "premium-streaming"; }
}

public class StreamingFactory {
    public StreamingProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new StreamingPremiumProduct();
        return new StreamingBasicProduct();
    }
}
