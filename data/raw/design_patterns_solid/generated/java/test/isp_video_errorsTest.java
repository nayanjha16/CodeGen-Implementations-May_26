package org.example.patterns;
public class VideoIspTest {
    public static void main(String[] args) {
        VideoStore st = new VideoStore();
        st.write("x");
        if (!VideoIspClient.mirror(st).equals("video:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
