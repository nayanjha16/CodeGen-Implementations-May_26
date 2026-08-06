package org.example.patterns;
public class LoggingDipTest {
    public static void main(String[] args) {
        String out = new LoggingAppService(new LoggingHttpGateway()).publish("p");
        if (!out.equals("http-logging:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
