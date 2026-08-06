package org.example.patterns;
public class SchedulingAbstractFactoryTest {
    public static void main(String[] args) {
        String out = SchedulingAbstractFactoryDemo.run(new SchedulingCloudFactory());
        if (!out.equals("cloud-btn-scheduling|cloud-dlg-scheduling")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
