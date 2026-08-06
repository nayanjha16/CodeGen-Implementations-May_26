package org.example.patterns;
public class WidgetsAbstractFactoryTest {
    public static void main(String[] args) {
        String out = WidgetsAbstractFactoryDemo.run(new WidgetsCloudFactory());
        if (!out.equals("cloud-btn-widgets|cloud-dlg-widgets")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
