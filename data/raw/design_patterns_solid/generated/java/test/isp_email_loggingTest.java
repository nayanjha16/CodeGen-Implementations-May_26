package org.example.patterns;
public class EmailIspTest {
    public static void main(String[] args) {
        EmailStore st = new EmailStore();
        st.write("x");
        if (!EmailIspClient.mirror(st).equals("email:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
