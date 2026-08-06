package org.example.patterns;
public class MapPrototypeTest {
    public static void main(String[] args) {
        MapPrototype a = new MapPrototype("map", 2);
        MapPrototype b = a.copy();
        b.setLabel("map-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
