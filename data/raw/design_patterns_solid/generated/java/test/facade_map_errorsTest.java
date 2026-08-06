package org.example.patterns;
public class MapFacadeTest {
    public static void main(String[] args) {
        MapFacade f = new MapFacade();
        if (!f.submit("x").equals("wrote-map:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
