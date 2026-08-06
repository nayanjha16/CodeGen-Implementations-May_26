package org.example.patterns;
public class HttpIspTest {
    public static void main(String[] args) {
        HttpStore st = new HttpStore();
        st.write("x");
        if (!HttpIspClient.mirror(st).equals("http:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
