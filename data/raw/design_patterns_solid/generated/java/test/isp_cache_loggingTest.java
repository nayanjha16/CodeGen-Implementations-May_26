package org.example.patterns;
public class CacheIspTest {
    public static void main(String[] args) {
        CacheStore st = new CacheStore();
        st.write("x");
        if (!CacheIspClient.mirror(st).equals("cache:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
