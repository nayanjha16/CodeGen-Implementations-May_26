package org.example.patterns;
public class HttpSrpTest {
    public static void main(String[] args) {
        HttpRecord r = new HttpRecord("a", 3);
        if (!new HttpFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
