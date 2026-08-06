package org.example.patterns;
public class MapIteratorTest {
    public static void main(String[] args) {
        MapCollection col = new MapCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("map:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
