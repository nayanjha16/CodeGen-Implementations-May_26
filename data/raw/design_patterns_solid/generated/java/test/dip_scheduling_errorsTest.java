package org.example.patterns;
public class SchedulingDipTest {
    public static void main(String[] args) {
        String out = new SchedulingAppService(new SchedulingHttpGateway()).publish("p");
        if (!out.equals("http-scheduling:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
