package org.example.patterns;
public class MapFactoryTest {
    public static void main(String[] args) {
        MapFactory f = new MapFactory();
        if (!f.create("basic").operate().equals("basic-map")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-map")) throw new AssertionError();
        System.out.println("ok");
    }
}
