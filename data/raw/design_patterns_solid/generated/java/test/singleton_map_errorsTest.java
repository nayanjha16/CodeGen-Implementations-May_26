package org.example.patterns;
public class MapSingletonTest {
    public static void main(String[] args) {
        MapSingleton a = MapSingleton.getInstance();
        MapSingleton b = MapSingleton.getInstance();
        a.setValue("map-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("map-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
