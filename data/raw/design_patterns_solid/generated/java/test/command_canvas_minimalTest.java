package org.example.patterns;
public class CanvasCommandTest {
    public static void main(String[] args) {
        CanvasCommand cmd = new CanvasActionCommand(new CanvasReceiver(), "x");
        if (!cmd.execute().equals("done-canvas:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
