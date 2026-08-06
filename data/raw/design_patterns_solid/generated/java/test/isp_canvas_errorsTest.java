package org.example.patterns;
public class CanvasIspTest {
    public static void main(String[] args) {
        CanvasStore st = new CanvasStore();
        st.write("x");
        if (!CanvasIspClient.mirror(st).equals("canvas:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
