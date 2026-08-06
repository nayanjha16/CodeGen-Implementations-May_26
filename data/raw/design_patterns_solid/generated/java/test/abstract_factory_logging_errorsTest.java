package org.example.patterns;
public class LoggingAbstractFactoryTest {
    public static void main(String[] args) {
        String out = LoggingAbstractFactoryDemo.run(new LoggingCloudFactory());
        if (!out.equals("cloud-btn-logging|cloud-dlg-logging")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
