package org.example.patterns;
public class AuthIspTest {
    public static void main(String[] args) {
        AuthStore st = new AuthStore();
        st.write("x");
        if (!AuthIspClient.mirror(st).equals("auth:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
