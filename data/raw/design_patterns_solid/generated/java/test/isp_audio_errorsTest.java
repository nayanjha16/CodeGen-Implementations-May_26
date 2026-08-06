package org.example.patterns;
public class AudioIspTest {
    public static void main(String[] args) {
        AudioStore st = new AudioStore();
        st.write("x");
        if (!AudioIspClient.mirror(st).equals("audio:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
