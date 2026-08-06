package org.example.patterns;
public class CanvasIteratorTest {
    public static void main(String[] args) {
        CanvasCollection col = new CanvasCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("canvas:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
