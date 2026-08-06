package org.example.patterns;
public class CanvasPrototypeTest {
    public static void main(String[] args) {
        CanvasPrototype a = new CanvasPrototype("canvas", 2);
        CanvasPrototype b = a.copy();
        b.setLabel("canvas-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
