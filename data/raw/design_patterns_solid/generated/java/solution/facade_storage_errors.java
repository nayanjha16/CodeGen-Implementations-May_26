// DesignPatternsSolid | kind=design_pattern | label=facade | domain=storage | tier=errors
package org.example.patterns;

class StorageValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class StorageWriter {
    public String write(String v) { return "wrote-storage:" + v; }
}
public class StorageFacade {
    private final StorageValidator validator = new StorageValidator();
    private final StorageWriter writer = new StorageWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
