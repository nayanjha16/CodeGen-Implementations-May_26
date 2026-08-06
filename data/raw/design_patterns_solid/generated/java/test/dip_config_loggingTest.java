package org.example.patterns;
public class ConfigDipTest {
    public static void main(String[] args) {
        String out = new ConfigAppService(new ConfigHttpGateway()).publish("p");
        if (!out.equals("http-config:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
