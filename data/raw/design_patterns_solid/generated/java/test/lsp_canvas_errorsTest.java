package org.example.patterns;
public class CanvasLspTest {
    public static void main(String[] args) {
        CanvasShape[] arr = new CanvasShape[] { new CanvasRectangle(2,3), new CanvasSquare(4) };
        if (CanvasLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
