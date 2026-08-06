package org.example.patterns;
public class SensorsAbstractFactoryTest {
    public static void main(String[] args) {
        String out = SensorsAbstractFactoryDemo.run(new SensorsCloudFactory());
        if (!out.equals("cloud-btn-sensors|cloud-dlg-sensors")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
