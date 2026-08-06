package org.example.patterns;
public class ReportAbstractFactoryTest {
    public static void main(String[] args) {
        String out = ReportAbstractFactoryDemo.run(new ReportCloudFactory());
        if (!out.equals("cloud-btn-report|cloud-dlg-report")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
