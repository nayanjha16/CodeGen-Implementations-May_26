package org.example.patterns;
public class CanvasAbstractFactoryTest {
    public static void main(String[] args) {
        String out = CanvasAbstractFactoryDemo.run(new CanvasCloudFactory());
        if (!out.equals("cloud-btn-canvas|cloud-dlg-canvas")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
