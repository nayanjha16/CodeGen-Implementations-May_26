package org.example.patterns;
public class MapIspTest {
    public static void main(String[] args) {
        MapStore st = new MapStore();
        st.write("x");
        if (!MapIspClient.mirror(st).equals("map:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
