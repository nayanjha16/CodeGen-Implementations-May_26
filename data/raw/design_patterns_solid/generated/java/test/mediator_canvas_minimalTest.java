package org.example.patterns;
public class CanvasMediatorTest {
    public static void main(String[] args) {
        CanvasMediator m = new CanvasMediator();
        new CanvasColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
