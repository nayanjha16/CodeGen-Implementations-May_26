package org.example.patterns;
public class CanvasSingletonTest {
    public static void main(String[] args) {
        CanvasSingleton a = CanvasSingleton.getInstance();
        CanvasSingleton b = CanvasSingleton.getInstance();
        a.setValue("canvas-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("canvas-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
