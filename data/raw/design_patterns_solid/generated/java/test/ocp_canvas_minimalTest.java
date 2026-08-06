package org.example.patterns;
public class CanvasOcpTest {
    public static void main(String[] args) {
        if (new CanvasPriceEngine(new CanvasTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
