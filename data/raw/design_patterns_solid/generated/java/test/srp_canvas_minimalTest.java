package org.example.patterns;
public class CanvasSrpTest {
    public static void main(String[] args) {
        CanvasRecord r = new CanvasRecord("a", 3);
        if (!new CanvasFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
