package org.example.patterns;
public class CanvasDipTest {
    public static void main(String[] args) {
        String out = new CanvasAppService(new CanvasHttpGateway()).publish("p");
        if (!out.equals("http-canvas:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
