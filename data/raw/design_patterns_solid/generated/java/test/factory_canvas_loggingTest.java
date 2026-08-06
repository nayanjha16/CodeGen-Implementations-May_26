package org.example.patterns;
public class CanvasFactoryTest {
    public static void main(String[] args) {
        CanvasFactory f = new CanvasFactory();
        if (!f.create("basic").operate().equals("basic-canvas")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-canvas")) throw new AssertionError();
        System.out.println("ok");
    }
}
