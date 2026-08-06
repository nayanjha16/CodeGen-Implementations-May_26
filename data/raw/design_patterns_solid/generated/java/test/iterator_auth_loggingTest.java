package org.example.patterns;
public class AuthIteratorTest {
    public static void main(String[] args) {
        AuthCollection col = new AuthCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("auth:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
