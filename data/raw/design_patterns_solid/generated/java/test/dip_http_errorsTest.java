package org.example.patterns;
public class HttpDipTest {
    public static void main(String[] args) {
        String out = new HttpAppService(new HttpHttpGateway()).publish("p");
        if (!out.equals("http-http:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
