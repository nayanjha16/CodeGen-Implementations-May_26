package org.example.patterns;
public class SessionIspTest {
    public static void main(String[] args) {
        SessionStore st = new SessionStore();
        st.write("x");
        if (!SessionIspClient.mirror(st).equals("session:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
