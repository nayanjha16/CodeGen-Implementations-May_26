package org.example.patterns;
public class CanvasMementoTest {
    public static void main(String[] args) {
        CanvasOriginator o = new CanvasOriginator();
        CanvasMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("canvas-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
