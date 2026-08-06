package org.example.patterns;
public class MapDipTest {
    public static void main(String[] args) {
        String out = new MapAppService(new MapHttpGateway()).publish("p");
        if (!out.equals("http-map:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
