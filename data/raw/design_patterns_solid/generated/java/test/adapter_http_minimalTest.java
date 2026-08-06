package org.example.patterns;
public class HttpAdapterTest {
    public static void main(String[] args) {
        HttpTarget t = new HttpAdapter(new HttpLegacyApi());
        if (!t.fetch().equals("modern-http")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
