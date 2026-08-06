package org.example.patterns;
public class DatabasePrototypeTest {
    public static void main(String[] args) {
        DatabasePrototype a = new DatabasePrototype("database", 2);
        DatabasePrototype b = a.copy();
        b.setLabel("database-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
