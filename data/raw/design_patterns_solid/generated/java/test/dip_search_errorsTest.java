package org.example.patterns;
public class SearchDipTest {
    public static void main(String[] args) {
        String out = new SearchAppService(new SearchHttpGateway()).publish("p");
        if (!out.equals("http-search:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
