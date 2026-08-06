package org.example.patterns;
public class MetricsAbstractFactoryTest {
    public static void main(String[] args) {
        String out = MetricsAbstractFactoryDemo.run(new MetricsCloudFactory());
        if (!out.equals("cloud-btn-metrics|cloud-dlg-metrics")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
