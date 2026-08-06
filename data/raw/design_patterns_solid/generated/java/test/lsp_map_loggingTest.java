package org.example.patterns;
public class MapLspTest {
    public static void main(String[] args) {
        MapShape[] arr = new MapShape[] { new MapRectangle(2,3), new MapSquare(4) };
        if (MapLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
