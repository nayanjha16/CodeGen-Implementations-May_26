package org.example.patterns;
public class ProfileIspTest {
    public static void main(String[] args) {
        ProfileStore st = new ProfileStore();
        st.write("x");
        if (!ProfileIspClient.mirror(st).equals("profile:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
